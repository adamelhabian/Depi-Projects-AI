
import streamlit as st
from utility.helpers import *
from datetime import date,time
from models.appointment import Appointment

# =========================================================
# Appointment Management
# =========================================================
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments = st.session_state.appointments


def show_appointment_management():
    st.title("📅 Appointment Management")

    tab1, tab2, tab3 = st.tabs(
        [
            "📅 Book",
            "❌ Cancel",
            "👀 View Active",
        ]
    )

    with tab1:
        st.subheader("Book New Appointment")

        if not patients:
            st.warning("Please register at least one patient first.")
        elif not staff_members:
            st.warning("Please add at least one doctor first.")
        else:
            patient_options = {
                f"{p.name} (ID: {get_entity_id(p)})": p
                for p in patients
            }

            doctor_options = {
                f"Dr. {d.name} ({d.specialization})": d
                for d in staff_members
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

                reason = st.text_input("Reason")

                submitted = st.form_submit_button("🎉 Book Appointment")

                if submitted:
                    selected_patient = patient_options[selected_patient_label]
                    selected_doctor = doctor_options[selected_doctor_label]

                    app = Appointment(
                        id=5000 + len(appointments) + 1,
                        date=appointment_date.isoformat(),
                        time=appointment_time.strftime("%I:%M %p"),
                        reason=reason,
                        patient=selected_patient,
                        doctor=selected_doctor,
                    )

                    appointments.append(app)

                    st.success(
                        f"Appointment #{app.id} booked successfully!"
                    )


    with tab2:
        st.subheader("Cancel Appointment")

        # Get only active appointments
        active_appointments = [
            appointment
            for appointment in appointments
            if appointment.status != "Cancelled"
        ]

        if not active_appointments:
            st.info("No active appointments found.")

        else:
            appointment_options = {
                f"#{appointment.id} - "
                f"{appointment.patient.name} - "
                f"{appointment.date} at {appointment.time}":
                appointment
                for appointment in active_appointments
            }

            selected_label = st.selectbox(
                "Select Appointment",
                list(appointment_options.keys()),
                key="cancel_appointment",
            )

            selected_appointment = appointment_options[selected_label]

            if st.button("❌ Cancel Appointment"):

                cancelled_id = selected_appointment.id

                # Change appointment status to Cancelled
                selected_appointment.cancel()

                st.success(
                    f"Appointment #{cancelled_id} cancelled successfully!"
                )

                # Re-run Streamlit to refresh the UI
                st.rerun()
            
    with tab3:
        st.subheader("Active Appointments")

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment.status != "Cancelled"
        ]

        if not active_appointments:
            st.info("No active appointments.")

        else:
            for appointment in active_appointments:
                with st.container(border=True):
                    st.write(f"### 📅 Appointment #{appointment.id}")
                    st.write(
                        f"**Patient:** {appointment.patient.name}"
                    )
                    st.write(
                        f"**Doctor:** Dr. {appointment.doctor.name}"
                    )
                    st.write(
                        f"**Date:** {appointment.date}"
                    )
                    st.write(
                        f"**Time:** {appointment.time}"
                    )
                    st.write(
                        f"**Reason:** {appointment.reason}"
                    )
                    st.write(
                        f"**Status:** {appointment.status}"
                    )
