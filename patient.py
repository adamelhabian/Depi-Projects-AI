"""
Hospital Management System - Patient & Person Module
Implements Person base class and Patient derived class following OOP principles.
"""

from datetime import datetime
from typing import List, Dict


class Person:
    """Base class representing a person with encapsulation and data validation."""

    def __init__(self, name: str, age: int):
        self._name = name.strip()
        self.age = age  # Triggers the age setter for validation

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if not isinstance(value, int) or value <= 0 or value > 120:
            raise ValueError("Age must be a valid positive integer between 1 and 120.")
        self._age = value

    def view_info(self) -> str:
        """Return basic personal information (UML-compliant)."""
        return f"Name: {self.name} | Age: {self.age}"

    def __str__(self) -> str:
        return self.view_info()


class Patient(Person):
    """Patient class extending Person, managing medical history and status."""

    # Internal class variable to generate unique patient IDs
    _id_counter: int = 1000

    def __init__(self, name: str, age: int, medical_record: str, status: str = "Active"):
        super().__init__(name, age)

        Patient._id_counter += 1
        self.patient_id: str = f"P-{Patient._id_counter}"
        self.status: str = status

        # List to store timestamped medical history records
        self._medical_history: List[Dict[str, str]] = []
        if medical_record:
            self.add_record(medical_record)

    @property
    def medical_record(self) -> str:
        """Return the most recent medical record entry for UML compatibility."""
        if not self._medical_history:
            return "No medical records found."
        return self._medical_history[-1]["details"]

    def add_record(self, details: str) -> None:
        """Add a new timestamped medical diagnosis or record entry."""
        if not details or not details.strip():
            raise ValueError("Record details cannot be empty.")

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "details": details.strip()
        }
        self._medical_history.append(entry)

    def view_record(self) -> str:
        """Display the patient's latest medical record (UML-compliant)."""
        return f"[{self.patient_id}] {self.name} | Latest Record: {self.medical_record}"

    def view_full_history(self) -> str:
        """Return the formatted comprehensive medical history."""
        header = f"\n=== Medical History for {self.name} (ID: {self.patient_id}) ==="
        if not self._medical_history:
            return f"{header}\nNo entries recorded."

        history_lines = [
            f"- [{entry['timestamp']}] {entry['details']}"
            for entry in self._medical_history
        ]
        return f"{header}\n" + "\n".join(history_lines)

    def update_status(self, new_status: str) -> None:
        """Update the patient's admission or treatment status."""
        self.status = new_status

    def __repr__(self) -> str:
        return f"Patient(id='{self.patient_id}', name='{self.name}', age={self.age}, status='{self.status}')"


if __name__ == "__main__":
    print("==========================================")
    print("  Hospital System - Patient Module Demo  ")
    print("==========================================\n")

    # 1. Instantiate a new patient
    patient1 = Patient(
        name="Ali Hassan",
        age=28,
        medical_record="Initial Diagnosis: Type 1 Diabetes"
    )

    # 2. Test UML methods
    print("1. Standard UML Outputs:")
    print(patient1.view_info())
    print(patient1.view_record())

    # 3. Add follow-up medical records
    print("\n2. Updating Medical History & Status:")
    patient1.add_record("Follow-up: Prescribed Metformin & custom diet plan")
    patient1.add_record("Checkup: Blood sugar stabilized")
    patient1.update_status("Stable")

    # 4. View full history
    print(patient1.view_full_history())