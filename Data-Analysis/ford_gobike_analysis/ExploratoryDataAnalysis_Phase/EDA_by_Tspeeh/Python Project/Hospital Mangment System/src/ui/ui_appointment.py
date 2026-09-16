import streamlit as st
from utility.helpers import *
from datetime import date, time, datetime
from models.appointment import Appointment

# =========================================================
# Appointment Management UI
# =========================================================

def show_appointment_management():
    patients = st.session_state.patients
    staff_members = st.session_state.staff_members
    appointments = st.session_state.appointments

    st.title("📅 Appointment Management")

    tab1, tab2, tab3 = st.tabs(
        [
            "📅 Book Appointment",
            "👀 View Active & Edit",
            "❌ Cancel Appointment",
        ]
    )

    # =========================================================
    # TAB 1: BOOK APPOINTMENT
    # =========================================================
    with tab1:
        st.subheader("Book New Appointment")

        if not patients:
            st.warning("Please register at least one patient first.")
        elif not staff_members:
            st.warning("Please add at least one doctor first.")
        else:
            patient_options = {
                f"{p.name} (ID: {get_entity_id(p)})": p for p in patients
            }

            doctor_options = {
                f"Dr. {d.name} ({getattr(d, 'specialization', 'General')})": d for d in staff_members
            }

            with st.form("book_appointment_form"):
                selected_patient_label = st.selectbox(
                    "Select Patient",
                    list(patient_options.keys()),
                )

                selected_doctor_label = st.selectbox(
                    "Select Doctor",
                    list(doctor_options.keys()),
                )

                appointment_date = st.date_input(
                    "Date",
                    value=date.today(),
                )

                appointment_time = st.time_input(
                    "Time",
                    value=time(10, 30),
                )

                reason = st.text_input("Reason / Notes", placeholder="e.g. Routine Checkup")

                submitted = st.form_submit_button("🎉 Book Appointment")

                if submitted:
                    selected_patient = patient_options[selected_patient_label]
                    selected_doctor = doctor_options[selected_doctor_label]

                    app = Appointment(
                        id=5000 + len(appointments) + 1,
                        date=appointment_date.isoformat(),
                        time=appointment_time.strftime("%I:%M %p"),
                        reason=reason if reason.strip() else "General Checkup",
                        patient=selected_patient,
                        doctor=selected_doctor,
                    )

                    appointments.append(app)
                    st.success(f"Appointment #{app.id} booked successfully!", icon="💯")

    # =========================================================
    # TAB 2: VIEW ACTIVE & INLINE EDIT
    # =========================================================
    with tab2:
        st.subheader("Active Appointments")

        active_appointments = [
            app for app in appointments if app.status != "Cancelled"
        ]

        if not active_appointments:
            st.info("No active appointments found.")
        else:
            for index, app in enumerate(active_appointments):
                with st.container(border=True):
                    col_info, col_edit, col_del = st.columns([5, 1, 1])

                    with col_info:
                        st.markdown(f"**Appointment #{app.id}** | Status: `{app.status}`")
                        st.write(f"👤 **Patient:** {app.patient.name} | 👨‍⚕️ **Doctor:** Dr. {app.doctor.name}")
                        st.caption(f"📅 **Date:** {app.date} | ⏰ **Time:** {app.time} | 📝 **Reason:** {app.reason}")

                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_app_btn_{app.id}_{index}"):
                            st.session_state[f"edit_app_mode_{app.id}"] = not st.session_state.get(f"edit_app_mode_{app.id}", False)

                    with col_del:
                        if st.button("❌", key=f"cancel_app_btn_{app.id}_{index}", type="primary", help="Cancel Appointment"):
                            app.cancel()
                            st.success(f"Appointment #{app.id} cancelled!")
                            st.rerun()

                    # Inline Edit Form
                    if st.session_state.get(f"edit_app_mode_{app.id}", False):
                        with st.form(key=f"form_edit_app_{app.id}_{index}"):
                            st.write(f"✏️ **Reschedule / Edit Appointment #{app.id}**")
                            
                            # Parse current date if possible
                            try:
                                curr_date = datetime.strptime(app.date, "%Y-%m-%d").date()
                            except:
                                curr_date = date.today()

                            new_date = st.date_input("New Date", value=curr_date, key=f"d_{app.id}")
                            new_time = st.time_input("New Time", value=time(10, 0), key=f"t_{app.id}")
                            new_reason = st.text_input("Reason", value=app.reason, key=f"r_{app.id}")
                            
                            # Doctor reassignment option
                            doctor_map = {f"Dr. {d.name} ({getattr(d, 'specialization', 'General')})": d for d in staff_members}
                            current_doc_key = [k for k, v in doctor_map.items() if v == app.doctor]
                            doc_idx = list(doctor_map.keys()).index(current_doc_key[0]) if current_doc_key else 0
                            new_doc_key = st.selectbox("Assigned Doctor", options=list(doctor_map.keys()), index=doc_idx, key=f"doc_{app.id}")

                            save_btn = st.form_submit_button("💾 Save Changes")

                            if save_btn:
                                # Update model using reschedule method
                                app.reschedule(new_date.isoformat(), new_time.strftime("%I:%M %p"))
                                app._reason = new_reason
                                app._doctor = doctor_map[new_doc_key]

                                st.session_state[f"edit_app_mode_{app.id}"] = False
                                st.rerun()

    # =========================================================
    # TAB 3: CANCEL APPOINTMENT (QUICK SELECT)
    # =========================================================
    with tab3:
        st.subheader("Cancel Appointment")

        active_appointments = [
            app for app in appointments if app.status != "Cancelled"
        ]

        if not active_appointments:
            st.info("No active appointments found.")
        else:
            appointment_options = {
                f"#{app.id} - {app.patient.name} ({app.date} at {app.time})": app
                for app in active_appointments
            }

            selected_label = st.selectbox(
                "Select Appointment to Cancel",
                list(appointment_options.keys()),
                key="cancel_select_box",
            )

            selected_appointment = appointment_options[selected_label]

            if st.button("❌ Confirm Cancellation", type="primary"):
                cancelled_id = selected_appointment.id
                selected_appointment.cancel()

                st.success(f"Appointment #{cancelled_id} cancelled successfully!")
                st.rerun()