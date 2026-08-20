"""
Patient Model
Part of Hospital Management System
Location: src/models/patient.py
"""

from typing import List, Optional

try:
    from .person import Person
except ImportError:
    try:
        from person import Person
    except ImportError:
        class Person:
            def __init__(
                self,
                id: int,
                name: str,
                age: int,
                phone: str,
                email: Optional[str] = None,
                gender: str = "Unspecified"
            ):
                self.person_id = id
                self.name = name
                self.age = age
                self.gender = gender
                self.phone = phone
                self.email = email

            def get_info(self) -> str:
                return f"ID: {self.person_id} | Name: {self.name} | Age: {self.age} | Phone: {self.phone}"


class Patient(Person):
    """Patient class inheriting from Person, managing blood type and medical history."""

    def __init__(
        self,
        id: int,
        name: str,
        age: int,
        phone: str,
        email: Optional[str],
        blood_type: str,
        gender: str = "Unspecified"
    ):
        super().__init__(
            id=id,
            name=name,
            age=age,
            phone=phone,
            email=email,
            gender=gender
        )

        self._blood_type: str = blood_type
        self._medical_history: List[str] = []

    @property
    def blood_type(self) -> str:
        """Return the patient's blood type."""
        return self._blood_type

    def add_medical_record(self, record: str) -> None:
        """Add a new medical record or diagnosis to the patient's history."""
        if not record or not str(record).strip():
            raise ValueError("Medical record cannot be empty.")
        self._medical_history.append(record.strip())

    def get_medical_history(self) -> List[str]:
        """Return a copy of the medical history list."""
        return self._medical_history.copy()

    def get_info(self) -> str:
        """Override get_info to include patient-specific information."""
        base_info = super().get_info()
        history_display = (
            ", ".join(self._medical_history)
            if self._medical_history
            else "No records"
        )
        return (
            f"[Patient] {base_info} | Blood Type: {self.blood_type} | "
            f"Medical History: [{history_display}]"
        )

    def __repr__(self) -> str:
        return f"Patient(id={self.person_id}, name='{self.name}', blood_type='{self.blood_type}')"
