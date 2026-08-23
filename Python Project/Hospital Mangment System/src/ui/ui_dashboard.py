import streamlit as st

# =========================================================
# Dashboard
# =========================================================
hospital = st.session_state.hospital
departments = st.session_state.departments
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments  = st.session_state.appointments

cardiology = st.session_state.departments[0]

def show_dashboard():
    st.title("🏥 Hospital Management System")
    st.subheader("📊 Admin Dashboard")

    st.write(
        "Welcome to the Hospital Management System. "
        "Use the sidebar to navigate between the different operations."
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👤 Patients", len(patients))

    with col2:
        st.metric("👨‍⚕️ Staff Members", len(staff_members))

    with col3:
        st.metric("📅 Appointments", len(appointments))

    with col4:
        st.metric(
            "🛏️ Cardiology",
            f"{cardiology.get_patient_count()}/{cardiology.capacity}",
        )

    st.divider()

    st.subheader("🏥 Hospital Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(f"**Name:** {hospital.name}")
        st.write(f"**Address:** {getattr(hospital, "_address", "N/A")}")
        st.write(f"**Phone:** {getattr(hospital, "_phone", "N/A")}")

    with info_col2:
        st.write(f"**Hospital Capacity:** {hospital.capacity}")
        st.write(f"**Departments:** {len(departments)}")
        st.write(f"**Active Appointments:** {len(appointments)}")