import streamlit as st
from utility.helpers import *
# =========================================================
# Medical Operations
# =========================================================


hospital = st.session_state.hospital
departments = st.session_state.departments
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments  = st.session_state.appointments

cardiology = st.session_state.departments[0]


def show_medical_operations():
    st.title("📋 Medical Operations")
    st.caption("Diagnose patients and prescribe medications.")

    if not patients:
        st.warning("No patients available for diagnosis.")
        return

    if not staff_members:
        st.warning("No doctors available.")
        return

    patient_options = {
        f"{p.name} (ID: {get_entity_id(p)})": p
        for p in patients
    }

    doctor_options = {
        f"Dr. {d.name}": d
        for d in staff_members
    }

    with st.form("medical_operation_form"):
        selected_patient_label = st.selectbox(
            "Select Patient",
            list(patient_options.keys()),
        )

        selected_doctor_label = st.selectbox(
            "Select Treating Doctor",
            list(doctor_options.keys()),
        )

        diagnosis = st.text_area("Medical Diagnosis")
        medications = st.text_area("Prescribed Medications")

        submitted = st.form_submit_button("✅ Update Medical Record")

        if submitted:
            target_patient = patient_options[selected_patient_label]
            doctor = doctor_options[selected_doctor_label]

            if not diagnosis or not medications:
                st.error("Please enter both diagnosis and medications.")
            else:
                doctor.diagnose(target_patient, diagnosis)
                doctor.prescribe(target_patient, medications)

                st.success(
                    f"Medical record updated for {target_patient.name}!"
                )

