from typing import List
from models.patient import Patient
from models.staff import Staff


class Department:
    """
    Department class managing hospital staff, patients, and unit capacity.
    """

    def __init__(self, id: int, name: str, location: str, capacity: int = 50):
        self._id = id
        self._name = name
        self._location = location
        self._capacity = capacity
        
        self._patients: List[Patient] = []
        self._staff: List[Staff] = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capacity(self) -> int:
        return self._capacity

    def add_patient(self, patient: Patient) -> None:
        if self.get_available_capacity() <= 0:
            raise ValueError(f"Department '{self._name}' is at full capacity!")
        
        if patient not in self._patients:
            self._patients.append(patient)

    def remove_patient(self, patient: Patient) -> None:
        if patient in self._patients:
            self._patients.remove(patient)

    def add_staff(self, staff_member: Staff) -> None:
        if staff_member not in self._staff:
            self._staff.append(staff_member)
            staff_member.assign_department(self)

    def remove_staff(self, staff_member: Staff) -> None:
        if staff_member in self._staff:
            self._staff.remove(staff_member)

    def get_patient_count(self) -> int:
        return len(self._patients)

    def get_staff_count(self) -> int:
        return len(self._staff)

    def get_available_capacity(self) -> int:
        return self._capacity - self.get_patient_count()

    def get_info(self) -> str:
        return (
            f"Department: {self._name} (ID: {self._id}) | Location: {self._location}\n"
            f"Capacity: {self.get_patient_count()}/{self._capacity} Patients "
            f"(Available: {self.get_available_capacity()}) | Staff Count: {self.get_staff_count()}"
        )