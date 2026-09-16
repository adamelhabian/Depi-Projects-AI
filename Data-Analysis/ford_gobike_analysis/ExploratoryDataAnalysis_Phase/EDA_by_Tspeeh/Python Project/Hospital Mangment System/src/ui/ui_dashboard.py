import streamlit as st
import pandas as pd
from utility.helpers import *

# =========================================================
# Dashboard Module
# =========================================================

def show_dashboard():
    hospital = st.session_state.hospital
    departments = st.session_state.departments
    patients = st.session_state.patients
    staff_members = st.session_state.staff_members
    appointments = st.session_state.appointments

    cardiology = departments[0] if departments else None

    st.title("🏥 Hospital Management System")
    st.subheader("📊 Admin Dashboard")

    st.write("Welcome to the Hospital Management System. Below is a real-time overview of patients and appointments.")

    st.divider()

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Total Patients", len(patients))
    with col2:
        st.metric("👨‍⚕️ Staff Members", len(staff_members))
    with col3:
        st.metric("📅 Total Appointments", len(appointments))
    with col4:
        cardio_count = cardiology.get_patient_count() if cardiology else 0
        cardio_cap = cardiology.capacity if cardiology else 0
        st.metric("🛏️ Cardiology Status", f"{cardio_count}/{cardio_cap}")

    st.divider()

    # =========================================================
    # SEARCH & FILTERED APPOINTMENTS TABLE
    # =========================================================
    st.subheader("🔍 Search & Filter Appointments / Patients")

    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

    with col_f1:
        search_query = st.text_input("🔎 Search by Patient Name or Phone", placeholder="Type patient name...")

    with col_f2:
        dept_names = ["All Departments"] + [d.name for d in departments]
        selected_dept = st.selectbox("🏢 Filter by Specialization", dept_names)

    with col_f3:
        status_filter = st.selectbox("📌 Visit Type / Status", ["All", "Scheduled", "Completed / Follow-up"])

    # Filter Appointments Logic
    filtered_apps = appointments.copy()

    if search_query:
        filtered_apps = [
            app for app in filtered_apps 
            if search_query.lower() in app.patient.name.lower() or search_query in str(app.patient.phone)
        ]

    if selected_dept != "All Departments":
        filtered_apps = [
            app for app in filtered_apps 
            if getattr(app.doctor, "specialization", "") == selected_dept
        ]

    if status_filter != "All":
        if status_filter == "Scheduled":
            filtered_apps = [app for app in filtered_apps if app.status == "Scheduled"]
        else:
            filtered_apps = [app for app in filtered_apps if "Follow-up" in str(app.time) or app.status == "Completed"]

    # Display Data Table
    if not filtered_apps:
        st.info("No appointments or records match the selected filters.")
    else:
        table_data = []
        for app in filtered_apps:
            p_id = get_entity_id(app.patient)
            table_data.append({
                "App ID": app.id,
                "Patient ID": p_id,
                "Patient Name": app.patient.name,
                "Blood Type": app.patient.blood_type,
                "Doctor": f"Dr. {app.doctor.name}",
                "Department": getattr(app.doctor, "specialization", "N/A"),
                "Date": app.date,
                "Time / Type": app.time,
                "Status": app.status,
                "Reason": app.reason
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # =========================================================
    # PATIENT QUICK LOOKUP & MEDICAL HISTORY
    # =========================================================
    st.subheader("📋 Patient Medical Details Lookup")

    if patients:
        patient_options = {f"{p.name} (ID: {get_entity_id(p)})": p for p in patients}
        selected_patient_key = st.selectbox("Select Patient to view complete records:", list(patient_options.keys()))
        selected_patient = patient_options[selected_patient_key]

        with st.expander(f"📑 Detailed Medical Record - {selected_patient.name}", expanded=True):
            p_col1, p_col2 = st.columns(2)
            
            with p_col1:
                st.write(f"**Full Name:** {selected_patient.name}")
                st.write(f"**Age:** {selected_patient.age}")
                st.write(f"**Phone:** {selected_patient.phone}")
                st.write(f"**Email:** {getattr(selected_patient, 'email', 'N/A')}")
                st.write(f"**Blood Type:** `{selected_patient.blood_type}`")

            with p_col2:
                # Medical History List
                history = selected_patient.get_medical_history()
                st.write("**🩺 Diagnosis & Medical History:**")
                if history:
                    for h in history:
                        st.markdown(f"- {h}")
                else:
                    st.caption("No medical records entered yet.")

                # Appointments for this specific patient
                p_id = get_entity_id(selected_patient)
                patient_apps = [app for app in appointments if get_entity_id(app.patient) == p_id]
                
                st.write("**📅 Appointments History:**")
                if patient_apps:
                    for app in patient_apps:
                        st.markdown(f"- **Dr. {app.doctor.name}** ({getattr(app.doctor, 'specialization', 'N/A')}) on `{app.date}` at `{app.time}` — *{app.reason}*")
                else:
                    st.caption("No booking history for this patient.")

    st.divider()

    # Hospital Summary
    st.subheader("🏥 Hospital Details")
    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(f"**Name:** {hospital.name}")
        st.write(f"**Address:** {getattr(hospital, '_address', 'N/A')}")
        st.write(f"**Phone:** {getattr(hospital, '_phone', 'N/A')}")

    with info_col2:
        st.write(f"**Hospital Capacity:** {hospital.capacity}")
        st.write(f"**Departments Count:** {len(departments)}")
        st.write(f"**Active Appointments:** {len(appointments)}")