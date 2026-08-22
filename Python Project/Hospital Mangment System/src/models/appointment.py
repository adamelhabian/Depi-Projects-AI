"""
Appointment Model
Location: src/models/appointment.py
"""

from typing import Optional
from models.patient import Patient
from models.doctor import Doctor


class Appointment:
    """
    Appointment class links a Patient with a Doctor and manages appointment states.
    """

    def __init__(
        self,
        id: int,
        date: str,
        time: str,
        reason: str,
        patient: Patient,
        doctor: Doctor,
        status: str = "Scheduled"
    ):
        self._id: int = id
        self._date: str = date
        self._time: str = time
        self._reason: str = reason
        self._patient: Patient = patient
        self._doctor: Doctor = doctor
        self._status: str = status

    @property
    def id(self) -> int:
        return self._id

    @property
    def date(self) -> str:
        return self._date

    @property
    def time(self) -> str:
        return self._time

    @property
    def status(self) -> str:
        return self._status

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def patient(self) -> Patient:
        return self._patient

    @property
    def doctor(self) -> Doctor:
        return self._doctor


    def schedule(self) -> None:
     
        self._status = "Scheduled"

    def cancel(self) -> None:
      
        self._status = "Cancelled"
        if hasattr(self._patient, 'appointments') and self in self._patient.appointments:
            self._patient.appointments.remove(self)

        
        if hasattr(self._doctor, 'appointments') and self in self._doctor.appointments:
            self._doctor.appointments.remove(self)

    def reschedule(self, new_date: str, new_time: str) -> None:
       
        self._date = new_date
        self._time = new_time
        self._status = "Rescheduled"

    def complete(self) -> None:
        
        self._status = "Completed"

    def get_info(self) -> str:
        
        return (
            f"Appointment ID: {self._id} | Status: {self._status}\n"
            f"Date & Time: {self._date} at {self._time}\n"
            f"Patient: {self._patient.name} (ID: {self._patient.person_id})\n"
            f"Doctor: Dr. {self._doctor.name} ({self._doctor.specialization})\n"
            f"Reason: {self._reason}"
        )