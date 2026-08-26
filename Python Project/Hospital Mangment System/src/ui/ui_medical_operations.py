import streamlit as st
from utility.helpers import *
from datetime import datetime

# =========================================================
# Medical Operations
# =========================================================

def show_medical_operations():
    patients = st.session_state.patients
    staff_members = st.session_state.staff_members

    st.title("📋 Medical Operations")
    st.caption("Diagnose patients and prescribe medications.")

    if not patients:
        st.warning("No patients available for diagnosis.")
        return

    if not staff_members:
        st.warning("No doctors available.")
        return

    patient_options = {
        f"{p.name} (ID: {get_entity_id(p)})": p for p in patients
    }

    doctor_options = {
        f"Dr. {d.name} ({getattr(d, 'specialization', 'General')})": d for d in staff_members
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

        diagnosis = st.text_area("Medical Diagnosis", placeholder="e.g. Acute Gastritis")
        medications = st.text_area("Prescribed Medications", placeholder="e.g. Antacid 20mg, Paracetamol 500mg")

        submitted = st.form_submit_button("✅ Update Medical Record")

        if submitted:
            target_patient = patient_options[selected_patient_label]
            doctor = doctor_options[selected_doctor_label]

            if not diagnosis or not medications:
                st.error("Please enter both diagnosis and medications.", icon="❌")
            else:
                # 1. Execute object methods if present
                if hasattr(doctor, "diagnose"):
                    doctor.diagnose(target_patient, diagnosis)
                if hasattr(doctor, "prescribe"):
                    doctor.prescribe(target_patient, medications)

                # 2. Formulate structured record with Timestamp & Doctor Info
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                formatted_record = (
                    f"**[{now_str}] Treated by Dr. {doctor.name}**\n"
                    f"- 🩸 **Diagnosis:** {diagnosis}\n"
                    f"- 💊 **Medications:** {medications}"
                )

                # Ensure medical history list exists and append
                if not hasattr(target_patient, "_medical_history") or target_patient._medical_history is None:
                    target_patient._medical_history = []

                target_patient.add_medical_record(formatted_record)

                st.success(f"Medical record successfully updated for {target_patient.name}!", icon="🎉")