from typing import Optional
from models.staff import Staff
from models.patient import Patient


class Doctor(Staff):
    """
    Doctor class inherits from Staff.
    Manages medical specialization, license number, diagnoses, and prescriptions.
    """

    def __init__(
        self,
        id: int,
        name: str,
        age: int,
        phone: str,
        email: Optional[str],
        salary: float,
        specialization: str,
        license_number: str,
        position: str = "Doctor"
    ):
       
        super().__init__(
            id=id,
            name=name,
            age=age,
            phone=phone,
            email=email,
            position=position,
            salary=salary
        )

        
        self._specialization: str = specialization
        self._license_number: str = license_number

    
    @property
    def specialization(self) -> str:
        return self._specialization

    @property
    def license_number(self) -> str:
        return self._license_number

    
    def diagnose(self, patient: Patient, diagnosis: str) -> None:
        
        record = f"Diagnosis by Dr. {self.name} ({self.specialization}): {diagnosis}"
        patient.add_medical_record(record)

    def prescribe(self, patient: Patient, medication: str) -> None:
        
        record = f"Prescription by Dr. {self.name}: {medication}"
        patient.add_medical_record(record)

    def get_info(self) -> str:
        
        base_info = super().get_info()
        return (
            f"[Doctor] {base_info} | Specialization: {self._specialization} | "
            f"License: {self._license_number}"
        )