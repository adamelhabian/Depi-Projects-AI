import streamlit as st
from models.doctor import Doctor
from models.departments import Department
from utility.helpers import *

# =========================================================
# Staff & Departments Management UI
# =========================================================

def show_staff_management():
    # Dynamic Access to Session State
    departments = st.session_state.departments
    staff_members = st.session_state.staff_members

    st.title("🏥 Staff & Department Management")

    # Main Tabs
    main_tab1, main_tab2 = st.tabs(["👥 Doctors Management", "🏢 Departments Management"])

    # =========================================================
    # TAB 1: DOCTORS MANAGEMENT
    # =========================================================
    with main_tab1:
        doc_tab1, doc_tab2 = st.tabs(["➕ Add Doctor", "👀 View Doctors"])

        # ------------------ Add Doctor ------------------
        with doc_tab1:
            st.subheader("Add New Doctor")

            dept_options = {dept.name: dept for dept in st.session_state.departments}

            if not dept_options:
                st.warning("⚠️ No departments available! Please create a department first in the 'Departments Management' tab.")
            
            with st.form("add_doctor_form"):
                name = st.text_input("Doctor Name")
                age = st.number_input("Age", min_value=1, max_value=120, value=30)
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                salary = st.number_input("Salary", min_value=0.0, value=10000.0, step=500.0)
                
                # Dynamic Selectbox directly from current state keys
                selected_dept_name = st.selectbox(
                    "Department / Specialization", 
                    options=list(dept_options.keys()) if dept_options else ["No Departments Available"]
                )

                license_number = st.text_input("License Number")

                submitted = st.form_submit_button("➕ Add Doctor")

                if submitted:
                    if not dept_options or selected_dept_name not in dept_options:
                        st.error("Please add a department first before adding a doctor!", icon="❌")
                    elif not name or not phone or not email or not license_number:
                        st.error("Please fill in all required fields.", icon="❌")
                    else:
                        chosen_dept = dept_options[selected_dept_name]
                        new_doc = Doctor(
                            id=100 + len(staff_members) + 1,
                            name=name,
                            age=age,
                            phone=phone,
                            email=email,
                            salary=salary,
                            specialization=chosen_dept.name,
                            license_number=license_number,
                        )

                        # Assign doctor to selected department
                        chosen_dept.add_staff(new_doc)
                        staff_members.append(new_doc)

                        st.success(f"Dr. {new_doc.name} added and assigned to {chosen_dept.name} department!", icon="💯")
                        st.rerun()

        # ------------------ View Doctors ------------------
        with doc_tab2:
            st.subheader("Current Staff Members")

            if not staff_members:
                st.info("No staff members found.")
            else:
                for index, staff in enumerate(staff_members):
                    doc_id = get_entity_id(staff)
                    
                    with st.container(border=True):
                        col_info, col_edit, col_del = st.columns([5, 1, 1])

                        with col_info:
                            spec = getattr(staff, "specialization", "N/A")
                            lic = getattr(staff, "license_number", "N/A")
                            sal = getattr(staff, "salary", 0.0)
                            st.markdown(f"**ID:** `{doc_id}` | **Dr. {staff.name}** | **Spec:** {spec} | **Salary:** ${sal:,.2f}")
                            st.caption(f"📞 {getattr(staff, 'phone', 'N/A')} | ✉️ {getattr(staff, 'email', 'N/A')} | 🪪 License: {lic}")

                        with col_edit:
                            if st.button("✏️ Edit", key=f"edit_doc_{doc_id}_{index}"):
                                st.session_state[f"edit_mode_doc_{doc_id}"] = not st.session_state.get(f"edit_mode_doc_{doc_id}", False)

                        with col_del:
                            if st.button("❌", key=f"del_doc_{doc_id}_{index}", type="primary", help="Delete Doctor"):
                                staff_members.remove(staff)
                                for dept in departments:
                                    dept.remove_staff(staff)
                                st.rerun()

                        # Inline Doctor Edit Form
                        if st.session_state.get(f"edit_mode_doc_{doc_id}", False):
                            with st.form(key=f"form_edit_doc_{doc_id}_{index}"):
                                st.write(f"✏️ **Edit Dr. {staff.name}**")
                                new_name = st.text_input("Name", value=staff.name)
                                new_age = st.number_input("Age", min_value=1, max_value=120, value=int(getattr(staff, "age", 30)))
                                new_phone = st.text_input("Phone", value=getattr(staff, "phone", ""))
                                new_email = st.text_input("Email", value=getattr(staff, "email", ""))
                                new_salary = st.number_input("Salary", min_value=0.0, value=float(getattr(staff, "salary", 0.0)), step=500.0)
                                new_license = st.text_input("License Number", value=getattr(staff, "license_number", ""))
                                
                                dept_names = [dept.name for dept in departments]
                                current_spec = getattr(staff, "specialization", dept_names[0] if dept_names else "")
                                default_idx = dept_names.index(current_spec) if current_spec in dept_names else 0
                                new_spec = st.selectbox("Department / Specialization", options=dept_names, index=default_idx)

                                save_btn = st.form_submit_button("💾 Save")

                                if save_btn:
                                    # Update Department internal staff list if department changed
                                    if current_spec != new_spec:
                                        for dept in departments:
                                            if dept.name == current_spec:
                                                dept.remove_staff(staff)
                                            if dept.name == new_spec:
                                                dept.add_staff(staff)

                                    staff.name = new_name
                                    staff.age = new_age
                                    staff.phone = new_phone
                                    staff.email = new_email
                                    staff._salary = new_salary
                                    staff._specialization = new_spec
                                    staff._license_number = new_license

                                    st.session_state[f"edit_mode_doc_{doc_id}"] = False
                                    st.rerun()

    # =========================================================
    # TAB 2: DEPARTMENTS MANAGEMENT
    # =========================================================
    with main_tab2:
        dept_tab1, dept_tab2 = st.tabs(["➕ Add Department", "👀 View Departments"])

        # ------------------ Add Department ------------------
        with dept_tab1:
            st.subheader("Add New Department")

            with st.form("add_department_form"):
                dept_name = st.text_input("Department Name", placeholder="e.g. Cardiology, Neurology")
                dept_location = st.text_input("Location / Floor", placeholder="e.g. Building A, 2nd Floor")
                dept_capacity = st.number_input("Patient Capacity", min_value=1, max_value=500, value=50, step=5)

                dept_submitted = st.form_submit_button("➕ Add Department")

                if dept_submitted:
                    if not dept_name or not dept_location:
                        st.error("Please fill in Department Name and Location.", icon="❌")
                    else:
                        new_dept = Department(
                            id=10 + len(departments) + 1,
                            name=dept_name,
                            location=dept_location,
                            capacity=dept_capacity
                        )
                        departments.append(new_dept)
                        st.success(f"Department '{new_dept.name}' created successfully!", icon="💯")
                        st.rerun()

        # ------------------ View Departments ------------------
        with dept_tab2:
            st.subheader("Current Departments")

            if not departments:
                st.info("No departments registered.")
            else:
                for index, dept in enumerate(departments):
                    dept_id = get_entity_id(dept)

                    with st.container(border=True):
                        col_info, col_edit, col_del = st.columns([5, 1, 1])

                        with col_info:
                            st.markdown(f"**ID:** `{dept.id}` | **Department:** {dept.name} | **Location:** {dept.location}")
                            st.caption(f"👥 Staff Count: {dept.get_staff_count()} | 🛌 Capacity: {dept.get_patient_count()}/{dept.capacity} (Available: {dept.get_available_capacity()})")

                        with col_edit:
                            if st.button("✏️ Edit", key=f"edit_dept_{dept_id}_{index}"):
                                st.session_state[f"edit_mode_dept_{dept_id}"] = not st.session_state.get(f"edit_mode_dept_{dept_id}", False)

                        with col_del:
                            if st.button("❌", key=f"del_dept_{dept_id}_{index}", type="primary", help="Delete Department"):
                                departments.remove(dept)
                                st.rerun()

                        # Inline Department Edit Form
                        if st.session_state.get(f"edit_mode_dept_{dept_id}", False):
                            with st.form(key=f"form_edit_dept_{dept_id}_{index}"):
                                st.write(f"✏️ **Edit Department: {dept.name}**")
                                edit_name = st.text_input("Department Name", value=dept.name)
                                edit_location = st.text_input("Location", value=dept.location)
                                edit_capacity = st.number_input("Capacity", min_value=1, max_value=500, value=int(dept.capacity))

                                save_dept_btn = st.form_submit_button("💾 Save")

                                if save_dept_btn:
                                    old_name = dept.name
                                    dept._name = edit_name
                                    dept._location = edit_location
                                    dept._capacity = edit_capacity

                                    # Update doctors specialization name if department name changes
                                    if old_name != edit_name:
                                        for doc in staff_members:
                                            if getattr(doc, "specialization", "") == old_name:
                                                doc._specialization = edit_name

                                    st.session_state[f"edit_mode_dept_{dept_id}"] = False
                                    st.rerun()