"""
Person Model
Location: src/models/person.py
"""

from typing import Optional


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

    def update_contact(self, phone: Optional[str] = None, email: Optional[str] = None) -> None:
       
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email