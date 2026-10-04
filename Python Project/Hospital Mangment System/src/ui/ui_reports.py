import streamlit as st
import pandas as pd
from utility.helpers import *

# =========================================================
# Reports & Analytics Module (Fixed Department Patient Counting)
# =========================================================

def show_reports():
    hospital = st.session_state.hospital
    departments = st.session_state.departments
    patients = st.session_state.patients
    staff_members = st.session_state.staff_members
    appointments = st.session_state.appointments

    st.title("📈 Hospital Reports")
    st.caption("Real-time data insights, department capacity, and appointment statistics.")

    # =========================================================
    # HOSPITAL GENERAL INFO
    # =========================================================
    st.subheader("🏥 Hospital Profile")

    try:
        st.info(hospital.get_info())
    except Exception:
        st.write(
            f"**Name:** {hospital.name}  \n"
            f"**Address:** {getattr(hospital, '_address', getattr(hospital, 'address', 'N/A'))}  \n"
            f"**Phone:** {getattr(hospital, '_phone', getattr(hospital, 'phone', 'N/A'))}"
        )

    # High-Level Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Total Patients", len(patients))
    with col2:
        st.metric("👨‍⚕️ Total Doctors/Staff", len(staff_members))
    with col3:
        st.metric("📅 Total Bookings", len(appointments))
    with col4:
        active_apps_count = len([a for a in appointments if a.status != "Cancelled"])
        st.metric("✅ Active Appointments", active_apps_count)

    st.divider()

    # Helper function to dynamically calculate real patients per department
    def get_real_dept_patient_count(dept):
        # 1. Check direct patient list inside department object
        direct_count = dept.get_patient_count() if hasattr(dept, "get_patient_count") else 0
        
        # 2. Count unique patients who have active appointments with doctors in this department
        dept_docs = [d for d in staff_members if getattr(d, "specialization", "") == dept.name]
        dept_patients_from_apps = {
            app.patient for app in appointments 
            if app.status != "Cancelled" and app.doctor in dept_docs
        }
        
        # Return maximum between direct list or active appointments list
        return max(direct_count, len(dept_patients_from_apps))

    # =========================================================
    # VISUAL ANALYTICS (NATIVE STREAMLIT)
    # =========================================================
    st.subheader("📊 Analytics Overview")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("**🏢 Department Occupancy Rate**")
        if departments:
            for dept in departments:
                count = get_real_dept_patient_count(dept)
                cap = dept.capacity
                ratio = min(count / cap, 1.0) if cap > 0 else 0.0
                
                st.write(f"**{dept.name}** ({count}/{cap} Patients)")
                st.progress(ratio)
        else:
            st.info("No department data available.")

    with chart_col2:
        st.write("**📌 Appointments Breakdown**")
        if appointments:
            status_counts = pd.Series([a.status for a in appointments]).value_counts()
            st.bar_chart(status_counts)
        else:
            st.info("No appointment data available.")

    st.divider()

    # =========================================================
    # DETAILED DEPARTMENTS REPORT
    # =========================================================
    st.subheader("🏢 Detailed Department Reports")

    if not departments:
        st.info("No departments registered.")
    else:
        for department in departments:
            count = get_real_dept_patient_count(department)
            available = max(0, department.capacity - count)

            with st.container(border=True):
                dept_col1, dept_col2 = st.columns([2, 1])

                with dept_col1:
                    st.write(f"### 🏢 {department.name}")
                    st.write(f"**📍 Location:** {department.location}")
                    st.write(f"**🛌 Occupancy Rate:** {count}/{department.capacity} Patients")
                    st.write(f"**👥 Assigned Staff:** {department.get_staff_count()} Doctors")

                with dept_col2:
                    st.metric("Beds Available", available)

                dept_staff = [s for s in staff_members if getattr(s, "specialization", "") == department.name]
                if dept_staff:
                    with st.expander("👨‍⚕️ View Assigned Doctors"):
                        for doc in dept_staff:
                            st.write(f"- **Dr. {doc.name}** | Phone: {doc.phone}")

    st.divider()