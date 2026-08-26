"""
Hospital Management System - Streamlit Admin Control Panel

Run:
    streamlit run streamlit_main.py
"""

import streamlit as st

# classes
from models.hospital import Hospital
from models.departments import Department
from models.doctor import Doctor
from models.patient import Patient
from models.staff import Staff
from models.appointment import Appointment


# UI



# =========================================================
# Page Configuration
# =========================================================
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
)


# =========================================================
# Session State / System Setup
# =========================================================
def initialize_system():
    """Initialize the hospital data once per Streamlit session."""
    if "hospital" not in st.session_state:
        hospital = Hospital(
            id=1,
            name="Al-Shifa International Hospital",
            address="Cairo",
            phone="0100000000",
            capacity=100,
        )

        cardiology = Department(
            id=101,
            name="Cardiology",
            location="Building A - Floor 2",
        )

        hospital.add_department(cardiology)

        # Default doctor from the original application
        dr_ahmed = Doctor(
            id=1,
            name="Ahmed Hassan",
            age=40,
            phone="01011111111",
            email="dr.ahmed@hospital.com",
            salary=15000.0,
            specialization="Cardiology",
            license_number="DOC-100",
        )

        cardiology.add_staff(dr_ahmed)

        st.session_state.hospital = hospital
        st.session_state.departments = [cardiology]
        st.session_state.patients = []
        st.session_state.staff_members = [dr_ahmed]
        st.session_state.appointments = []


def get_entity_id(obj):
    """Safely get an ID from Person / Staff / Doctor objects."""
    if hasattr(obj, "person_id"):
        return obj.person_id
    elif hasattr(obj, "id"):
        return obj.id
    elif hasattr(obj, "_id"):
        return obj._id
    return "N/A"


initialize_system()





hospital = st.session_state.hospital
departments = st.session_state.departments
patients = st.session_state.patients
staff_members = st.session_state.staff_members
appointments  = st.session_state.appointments

cardiology = st.session_state.departments[0]






from ui.ui_staffs_and_doctors import show_staff_management
from ui.ui_patient import show_patient_management
from ui.ui_dashboard import*
from ui.ui_reports import *
from ui.ui_appointment import*
from ui.ui_medical_operations import *





# =========================================================
# Sidebar Navigation
# =========================================================
with st.sidebar:
    st.title("🏥 Hospital System")
    st.caption("Admin Control Panel")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "👥 Staff & Doctors",
            "👤 Patients",
            "📅 Appointments",
            "📋 Medical Operations",
            "📈 Reports",
        ],
        index=0,
    )

    st.divider()

    st.subheader("Hospital")
    st.write(hospital.name)
    st.write(f"📍 {getattr(hospital, "_address", "N/A")}")
    st.write(f"🛏️ Capacity: {cardiology.get_patient_count()}/{cardiology.capacity}")

# =========================================================
# Main Router
# =========================================================
if page == "📊 Dashboard":
    show_dashboard()

elif page == "👥 Staff & Doctors":
    show_staff_management()

elif page == "👤 Patients":
    show_patient_management()

elif page == "📅 Appointments":
    show_appointment_management()

elif page == "📋 Medical Operations":
    show_medical_operations()

elif page == "📈 Reports":
    show_reports()
