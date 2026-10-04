import streamlit as st

from utility.helpers import *
from models.patient import Patient
from models.appointment import Appointment

# =========================================================
# Patient Management UI
# =========================================================

def show_patient_management():
    hospital = st.session_state.hospital
    departments = st.session_state.departments
    patients = st.session_state.patients
    staff_members = st.session_state.staff_members
    appointments = st.session_state.appointments

    cardiology = departments[0] if departments else None

    st.title("👤 Patient Management")

    tab1, tab2, tab3 = st.tabs(["➕ Register Patient", "👀 View Patients", "📅 Book Appointment"])

    # =========================================================
    # TAB 1: REGISTER PATIENT
    # =========================================================
    with tab1:
        st.subheader("Register New Patient")

        with st.form("register_patient_form"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            phone = st.text_input("Phone")
            email = st.text_input("Email (Optional)")
            blood = st.text_input("Blood Type", placeholder="e.g. A+")

            submitted = st.form_submit_button("➕ Register Patient")

            if submitted:
                if not name or not phone or not blood:
                    st.error("Please fill in all required fields (Name, Phone, Blood Type).", icon="❌")
                else:
                    new_patient = Patient(
                        id=1000 + len(patients) + 1,
                        name=name,
                        age=age,
                        phone=phone,
                        email=email or None,
                        blood_type=blood,
                    )

                    if cardiology:
                        cardiology.add_patient(new_patient)
                    patients.append(new_patient)

                    st.success(
                        f"Patient '{new_patient.name}' registered successfully! "
                        f"ID: {get_entity_id(new_patient)}",
                        icon="💯"
                    )

    # =========================================================
    # TAB 2: VIEW PATIENTS (WITH INLINE EDIT & DELETE)
    # =========================================================
    with tab2:
        st.subheader("Registered Patients")

        if not patients:
            st.info("No registered patients found.")
        else:
            for index, patient in enumerate(patients):
                p_id = get_entity_id(patient)
                
                with st.container(border=True):
                    # Action layout: Info on left, Edit & Delete on right
                    col_info, col_edit, col_del = st.columns([5, 1, 1])

                    with col_info:
                        st.markdown(f"**ID:** `{p_id}` | **Name:** {patient.name} | **Age:** {patient.age} | **Blood Type:** `{patient.blood_type}`")
                        
                        # Fetch appointments related to this patient
                        patient_apps = [app for app in appointments if getattr(app.patient, 'id', get_entity_id(app.patient)) == p_id]
                        app_summary = ", ".join([f"Dr. {app.doctor.name} ({app.date} @ {app.time})" for app in patient_apps]) if patient_apps else "None"

                        history = patient.get_medical_history()
                        history_text = ", ".join(history) if history else "No records"

                        st.caption(f"📞 {patient.phone} | ✉️ {getattr(patient, 'email', 'N/A')} | 📋 History: {history_text} | 📅 Bookings: {app_summary}")

                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_pat_{p_id}_{index}"):
                            st.session_state[f"edit_pat_mode_{p_id}"] = not st.session_state.get(f"edit_pat_mode_{p_id}", False)

                    with col_del:
                        if st.button("❌", key=f"del_pat_{p_id}_{index}", type="primary", help="Delete Patient"):
                            patients.remove(patient)
                            for dept in departments:
                                dept.remove_patient(patient)
                            # Remove related appointments when patient is deleted
                            appointments[:] = [app for app in appointments if getattr(app.patient, 'id', get_entity_id(app.patient)) != p_id]
                            st.rerun()

                    # Inline Edit Patient Form
                    if st.session_state.get(f"edit_pat_mode_{p_id}", False):
                        with st.form(key=f"form_edit_pat_{p_id}_{index}"):
                            st.write(f"✏️ **Edit Patient: {patient.name}**")
                            new_name = st.text_input("Patient Name", value=patient.name)
                            new_age = st.number_input("Age", min_value=0, max_value=120, value=int(patient.age))
                            new_phone = st.text_input("Phone", value=patient.phone)
                            new_email = st.text_input("Email", value=getattr(patient, "email", "") or "")
                            new_blood = st.text_input("Blood Type", value=patient.blood_type)

                            save_btn = st.form_submit_button("💾 Save")

                            if save_btn:
                                patient.name = new_name
                                patient.age = new_age
                                patient.phone = new_phone
                                patient.email = new_email or None
                                patient._blood_type = new_blood

                                st.session_state[f"edit_pat_mode_{p_id}"] = False
                                st.rerun()

   # =========================================================
    # TAB 3: ASSIGN DOCTOR / APPOINTMENT
    # =========================================================
    with tab3:
        st.subheader("Assign Doctor to Patient")

        if not patients:
            st.warning("No registered patients available.")
        elif not staff_members:
            st.warning("No doctors available in the system.")
        else:
            with st.form("assign_doctor_form"):
                patient_map = {f"{p.name} (ID: {get_entity_id(p)})": p for p in patients}
                doctor_map = {f"Dr. {d.name} ({getattr(d, 'specialization', 'General')})": d for d in staff_members}

                selected_patient_key = st.selectbox("Select Patient", options=list(patient_map.keys()))
                selected_doctor_key = st.selectbox("Assign Doctor", options=list(doctor_map.keys()))

                # Toggle between Follow-up (Immediate) and Scheduled Appointment
                visit_type = st.radio("Visit Type", options=["Immediate / Follow-up (متابعة عادية)", "Scheduled Appointment (حجز بموعد)"], horizontal=True)

                if "Scheduled" in visit_type:
                    col_date, col_time = st.columns(2)
                    with col_date:
                        app_date = str(st.date_input("Date"))
                    with col_time:
                        app_time = st.time_input("Time").strftime("%H:%M")
                else:
                    import datetime
                    app_date = str(datetime.date.today())
                    app_time = "Follow-up / Walk-in"

                reason = st.text_area("Reason / Notes", placeholder="e.g. Regular Follow-up, Routine checkup, Emergency")

                book_submitted = st.form_submit_button("✅ Assign Doctor")

                if book_submitted:
                    chosen_patient = patient_map[selected_patient_key]
                    chosen_doctor = doctor_map[selected_doctor_key]

                    new_app = Appointment(
                        id=5000 + len(appointments) + 1,
                        date=app_date,
                        time=app_time,
                        reason=reason if reason.strip() else "General Follow-up",
                        patient=chosen_patient,
                        doctor=chosen_doctor,
                        status="Completed" if "Follow-up" in visit_type else "Scheduled"
                    )

                    appointments.append(new_app)
                    st.success(f"Successfully assigned Dr. {chosen_doctor.name} to {chosen_patient.name}!", icon="🎉")