import streamlit as st

# =========================================================
# Reports
# =========================================================

hospital = st.session_state.hospital
departments = st.session_state.departments
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments  = st.session_state.appointments

cardiology = st.session_state.departments[0]


def show_reports():
    st.title("📈 Hospital Stats & Reports")

    st.subheader("Hospital System Report")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Patients", len(patients))

    with col2:
        st.metric("Staff Members", len(staff_members))

    with col3:
        st.metric("Appointments", len(appointments))

    with col4:
        st.metric(
            "Cardiology Capacity",
            f"{cardiology.get_patient_count()}/{cardiology.capacity}",
        )

    st.divider()

    st.subheader("🏥 Hospital Information")

    try:
        st.write(hospital.get_info())
    except Exception:
        st.write(
            f"{hospital.name} - {getattr(hospital, "_address", "N/A")} - "
            f"{getattr(hospital, "_phone", "N/A")}"
        )

    st.subheader("Departments")

    for department in departments:
        with st.container(border=True):
            st.write(f"### 🏢 {department.name}")
            st.write(f"**Location:** {department.location}")
            st.write(
                f"**Patients:** "
                f"{department.get_patient_count()}/{department.capacity}"
            )

