
from typing import Optional, TYPE_CHECKING
from models.person import Person

if TYPE_CHECKING:
    from models.departments import Department

class Staff(Person):
    """
    Staff is a subclass of Person and serves as the parent class for Doctor.
    """

    def __init__(
        self,
        id: int,
        name: str,
        age: int,
        phone: str,
        position: str,
        salary: float,
        email: Optional[str] = None,
        gender: str = "Unspecified",
        department: Optional[Department] = None
    ):
        super().__init__(
            id=id,
            name=name,
            age=age,
            phone=phone,
            email=email,
            gender=gender
        )

        self._position: str = position
        self._salary: float = salary
        self._department: Optional[Department] = department

    @property
    def position(self) -> str:
        return self._position

    @property
    def salary(self) -> float:
        return self._salary

    @property
    def department(self) -> Optional[Department]:
        return self._department

    def assign_department(self, department: Department) -> None:
        """Assign or change the staff member's department."""
        self._department = department

    def get_info(self) -> str:
        """Override get_info to include staff specifics."""
        base_info = super().get_info()
        dept_name = self._department.name if self._department else "None"
        return f"{base_info} | Position: {self._position} | Salary: ${self._salary:.2f} | Dept: {dept_name}"