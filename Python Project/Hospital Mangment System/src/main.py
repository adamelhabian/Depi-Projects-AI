"""
Hospital Management System - Admin Control Panel
Location: src/main.py
"""

from models.hospital import Hospital
from models.departments import Department
from models.doctor import Doctor
from models.patient import Patient
from models.staff import Staff
from models.appointment import Appointment


def admin_dashboard():
    # ---------------------------------------------------------
    # System Setup (Hospital & Base Department)
    # ---------------------------------------------------------
    hospital = Hospital(id=1, name="Al-Shifa International Hospital", address="Cairo", phone="0100000000", capacity=100)
    cardiology = Department(id=101, name="Cardiology", location="Building A - Floor 2")
    hospital.add_department(cardiology)

    # Database Collections
    departments = [cardiology]
    patients = []
    staff_members = []
    appointments = []

    # Helper function to get an entity's ID safely across Person / Staff / Doctor classes
    def get_entity_id(obj):
        if hasattr(obj, 'person_id'):
            return obj.person_id
        elif hasattr(obj, 'id'):
            return obj.id
        elif hasattr(obj, '_id'):
            return obj._id
        return "N/A"

    # Default Doctor Initialization
    dr_ahmed = Doctor(
        id=1, name="Ahmed Hassan", age=40, phone="01011111111", 
        email="dr.ahmed@hospital.com", salary=15000.0, 
        specialization="Cardiology", license_number="DOC-100"
    )
    cardiology.add_staff(dr_ahmed)
    staff_members.append(dr_ahmed)

    while True:
        print("\n" + "=" * 60)
        print("      🏥 HOSPITAL MANAGEMENT SYSTEM - ADMIN DASHBOARD 🏥      ")
        print("=" * 60)
        print("1. 👥 Manage Staff & Doctors")
        print("2. 👤 Manage Patients")
        print("3. 📅 Manage Appointments")
        print("4. 📋 Medical Operations (Diagnose & Prescribe)")
        print("5. 📊 View Hospital Stats & Reports")
        print("6. 🚪 Exit System")
        print("=" * 60)

        choice = input("Select an Admin Operation (1-6): ")

        # =========================================================
        # 1. MANAGE STAFF & DOCTORS
        # =========================================================
        if choice == "1":
            print("\n--- 👥 STAFF MANAGEMENT ---")
            print("1. Add New Doctor")
            print("2. View All Staff Members")
            sub_c = input("Select: ")

            if sub_c == "1":
                name = input("Doctor Name: ")
                age = int(input("Age: "))
                phone = input("Phone: ")
                email = input("Email: ")
                salary = float(input("Salary: "))
                spec = input("Specialization: ")
                lic = input("License Number: ")

                new_doc = Doctor(
                    id=100 + len(staff_members) + 1,
                    name=name, age=age, phone=phone, email=email,
                    salary=salary, specialization=spec, license_number=lic
                )
                cardiology.add_staff(new_doc)
                staff_members.append(new_doc)
                print(f"\n✅ Doctor Dr. {new_doc.name} added successfully!")

            elif sub_c == "2":
                print("\n--- Current Staff Members ---")
                for s in staff_members:
                    s_id = get_entity_id(s)
                    print(f"• ID: {s_id} | Name: Dr. {s.name} | Spec: {s.specialization} | Salary: ${s.salary}")

        # =========================================================
        # 2. MANAGE PATIENTS
        # =========================================================
        elif choice == "2":
            print("\n--- 👤 PATIENT MANAGEMENT ---")
            print("1. Register New Patient")
            print("2. View All Patients")
            sub_c = input("Select: ")

            if sub_c == "1":
                name = input("Patient Name: ")
                age = int(input("Age: "))
                phone = input("Phone: ")
                email = input("Email (Press Enter to skip): ") or None
                blood = input("Blood Type (e.g. A+): ")

                new_p = Patient(
                    id=1000 + len(patients) + 1,
                    name=name, age=age, phone=phone, email=email, blood_type=blood
                )
                cardiology.add_patient(new_p)
                patients.append(new_p)
                print(f"\n✅ Patient '{new_p.name}' registered successfully! (ID: {get_entity_id(new_p)})")

            elif sub_c == "2":
                if not patients:
                    print("\n⚠️ No registered patients.")
                else:
                    print("\n--- Registered Patients ---")
                    for p in patients:
                        p_id = get_entity_id(p)
                        print(f"• ID: {p_id} | Name: {p.name} | Age: {p.age} | Blood: {p.blood_type}")

        # =========================================================
        # 3. MANAGE APPOINTMENTS
        # =========================================================
        elif choice == "3":
            print("\n--- 📅 APPOINTMENT MANAGEMENT ---")
            print("1. Book New Appointment")
            print("2. Reschedule Appointment")
            print("3. Cancel Appointment")
            print("4. View Active Appointments")
            sub_c = input("Select: ")

            # Book
            if sub_c == "1":
                if not patients:
                    print("\n⚠️ Please register at least one patient first!")
                    continue

                print("\nSelect Patient:")
                for idx, p in enumerate(patients, 1):
                    p_id = get_entity_id(p)
                    print(f"  [{idx}] {p.name} (ID: {p_id})")
                p_idx = int(input("Patient Choice #: ")) - 1
                selected_patient = patients[p_idx]

                print("\nSelect Doctor:")
                for idx, d in enumerate(staff_members, 1):
                    print(f"  [{idx}] Dr. {d.name} ({d.specialization})")
                d_idx = int(input("Doctor Choice #: ")) - 1
                selected_doctor = staff_members[d_idx]

                date = input("Date (YYYY-MM-DD): ")
                time = input("Time (e.g., 10:30 AM): ")
                reason = input("Reason: ")

                app = Appointment(
                    id=5000 + len(appointments) + 1,
                    date=date, time=time, reason=reason,
                    patient=selected_patient, doctor=selected_doctor
                )
                appointments.append(app)
                print(f"\n🎉 Appointment #{app.id} booked successfully!")

            # Reschedule
            elif sub_c == "2":
                if not appointments:
                    print("\n⚠️ No appointments found.")
                    continue
                for idx, a in enumerate(appointments, 1):
                    print(f"  [{idx}] ID: {a.id} | Patient: {a.patient.name} | {a.date} at {a.time}")
                a_idx = int(input("Select Appointment #: ")) - 1
                
                new_d = input("New Date: ")
                new_t = input("New Time: ")
                appointments[a_idx].reschedule(new_d, new_t)
                print("\n🔄 Appointment rescheduled successfully!")

            # Cancel
            elif sub_c == "3":
                if not appointments:
                    print("\n⚠️ No appointments found.")
                    continue
                for idx, a in enumerate(appointments, 1):
                    print(f"  [{idx}] ID: {a.id} | Patient: {a.patient.name}")
                a_idx = int(input("Select Appointment #: ")) - 1
                
                cancelled_app = appointments.pop(a_idx)
                cancelled_app.cancel()
                print(f"\n❌ Appointment #{cancelled_app.id} cancelled and removed from active list!")

            # View
            elif sub_c == "4":
                if not appointments:
                    print("\n⚠️ No active appointments.")
                else:
                    print("\n--- Active Appointments ---")
                    for a in appointments:
                        print("-" * 40)
                        print(a.get_info())

        # =========================================================
        # 4. MEDICAL OPERATIONS
        # =========================================================
        elif choice == "4":
            if not patients:
                print("\n⚠️ No patients available for diagnosis!")
                continue

            print("\nSelect Patient for Treatment:")
            for idx, p in enumerate(patients, 1):
                p_id = get_entity_id(p)
                print(f"  [{idx}] {p.name} (ID: {p_id})")
            p_idx = int(input("Patient Choice #: ")) - 1
            target_p = patients[p_idx]

            print("\nSelect Treating Doctor:")
            for idx, d in enumerate(staff_members, 1):
                print(f"  [{idx}] Dr. {d.name}")
            d_idx = int(input("Doctor Choice #: ")) - 1
            doc = staff_members[d_idx]

            diag = input("Enter Medical Diagnosis: ")
            meds = input("Enter Prescribed Medications: ")

            doc.diagnose(target_p, diag)
            doc.prescribe(target_p, meds)

            print(f"\n✅ Medical Record Updated for {target_p.name}!")

        # =========================================================
        # 5. VIEW SYSTEM STATS & REPORTS
        # =========================================================
        elif choice == "5":
            print("\n--- 📊 HOSPITAL SYSTEM REPORT ---")
            print(hospital.get_info())
            print(f"• Registered Patients  : {len(patients)}")
            print(f"• Active Staff Members : {len(staff_members)}")
            print(f"• Total Appointments   : {len(appointments)}")
            print(f"• Cardiology Capacity  : {cardiology.get_patient_count()}/{cardiology.capacity}")

        # Exit
        elif choice == "6":
            print("\nExiting Admin Control Panel. System Shutting Down... 👋")
            break
        else:
            print("\nInvalid choice! Please select 1 to 6.")


if __name__ == "__main__":
    admin_dashboard()