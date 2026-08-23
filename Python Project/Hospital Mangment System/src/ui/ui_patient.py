import streamlit as st

from utility.helpers import*
from models.patient import Patient

# =========================================================
# Patient Management
# =========================================================


hospital = st.session_state.hospital
departments = st.session_state.departments
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments  = st.session_state.appointments

cardiology = st.session_state.departments[0]

def show_patient_management():
    st.title("👤 Patient Management")

    tab1, tab2 = st.tabs(["➕ Register Patient", "👀 View Patients"])

    with tab1:
        st.subheader("Register New Patient")

        with st.form("register_patient_form"):
            name = st.text_input("Patient Name")
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=25,
            )
            phone = st.text_input("Phone")
            email = st.text_input("Email (Optional)")
            blood = st.text_input("Blood Type", placeholder="e.g. A+")

            submitted = st.form_submit_button("➕ Register Patient")

            if submitted:
                if not name or not phone or not blood:
                    st.error("Please fill in the required fields.")
                else:
                    new_patient = Patient(
                        id=1000 + len(patients) + 1,
                        name=name,
                        age=age,
                        phone=phone,
                        email=email or None,
                        blood_type=blood,
                    )

                    cardiology.add_patient(new_patient)
                    patients.append(new_patient)

                    st.success(
                        f"Patient '{new_patient.name}' registered successfully! "
                        f"ID: {get_entity_id(new_patient)}"
                    )

    with tab2:
        st.subheader("Registered Patients")

        if not patients:
            st.info("No registered patients.")
        else:
            patient_data = []

            for patient in patients:
                patient_data.append(
                    {
                        "ID": get_entity_id(patient),
                        "Name": patient.name,
                        "Age": patient.age,
                        "Phone": patient.phone,
                        "Email": getattr(patient, "email", "N/A"),
                        "Blood Type": patient.blood_type,
                        "Diagnose patients and prescribe medications":patient.get_medical_history()
                    }
                )

            st.dataframe(
                patient_data,
                use_container_width=True,
                hide_index=True,
            )
