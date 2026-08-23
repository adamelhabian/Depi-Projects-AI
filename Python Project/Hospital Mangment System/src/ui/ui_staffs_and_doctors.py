import streamlit as st
from models.doctor import Doctor
from utility.helpers import *
# =========================================================
# Staff & Doctors
# =========================================================

# Session_states 
cardiology = st.session_state.departments[0]
staff_members = st.session_state.staff_members

def show_staff_management():
    st.title("👥 Staff & Doctors Management")

    tab1, tab2 = st.tabs(["➕ Add Doctor", "👀 View Staff"])

    with tab1:
        st.subheader("Add New Doctor")

        with st.form("add_doctor_form"):
            name = st.text_input("Doctor Name")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            salary = st.number_input(
                "Salary",
                min_value=0.0,
                value=10000.0,
                step=500.0,
            )
            specialization = st.text_input("Specialization")
            license_number = st.text_input("License Number")

            submitted = st.form_submit_button("➕ Add Doctor")

            if submitted:
                if not name or not phone or not email or not specialization or not license_number:
                    st.error("Please fill in all required fields.",icon="❌")
                else:
                    new_doc = Doctor(
                        id=100 + len(staff_members) + 1,
                        name=name,
                        age=age,
                        phone=phone,
                        email=email,
                        salary=salary,
                        specialization=specialization,
                        license_number=license_number,
                    )

                    cardiology.add_staff(new_doc)
                    staff_members.append(new_doc)

                    st.success(
                        f"Doctor Dr. {new_doc.name} added successfully!",icon="💯"
                    )

    with tab2:
        st.subheader("Current Staff Members")

        if not staff_members:
            st.info("No staff members found.")
        else:
            staff_data = []

            for staff in staff_members:
                staff_data.append(
                    {
                        "ID": get_entity_id(staff),
                        "Name": f"Dr. {staff.name}",
                        "Specialization": getattr(staff, "specialization", "N/A"),
                        "Salary": getattr(staff, "salary", "N/A"),
                        "Phone": getattr(staff, "phone", "N/A"),
                        "Email": getattr(staff, "email", "N/A"),
                    }
                )

            st.dataframe(
                staff_data,
                use_container_width=True,
                hide_index=True,
            )

