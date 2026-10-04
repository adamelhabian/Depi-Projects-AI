class Hospital:
    """Represent a hospital that manages departments, patients, and staff."""

    def __init__(
        self,
        id: int,
        name: str,
        address: str,
        phone: str,
        capacity: int
    ) -> None:
        """
        Initialize a hospital.

        Args:
            id: The unique identifier of the hospital.
            name: The name of the hospital.
            address: The physical address of the hospital.
            phone: The contact phone number of the hospital.
            capacity: The maximum number of patients the hospital can accommodate.
        """
        self._id = id
        self._name = name
        self._address = address
        self._phone = phone
        self._capacity = capacity
        self._departments = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capacity(self) -> int:
        return self._capacity

    def add_department(self, department: object) -> None:
        """
        Add a department to the hospital.

        Args:
            department: The department object to add.
        """
        if department not in self._departments:
            self._departments.append(department)

    def remove_department(self, department: object) -> None:
        """
        Remove a department from the hospital.

        Args:
            department: The department object to remove.
        """
        if department in self._departments:
            self._departments.remove(department)

    def get_department_count(self) -> int:
        """
        Return the number of departments in the hospital.

        Returns:
            The total number of departments.
        """
        return len(self._departments)

    def get_patient_count(self) -> int:
        """
        Return the number of patients across all departments.

        Returns:
            The total number of patients.
        """
        return sum(dept.get_patient_count() for dept in self._departments)

    def get_staff_count(self) -> int:
        """
        Return the number of staff members across all departments.

        Returns:
            The total number of staff members.
        """
        return sum(dept.get_staff_count() for dept in self._departments)

    def get_available_capacity(self) -> int:
        """
        Calculate the remaining patient capacity of the hospital.

        Returns:
            The number of available places for additional patients.
        """
        return self._capacity - self.get_patient_count()

    def get_info(self) -> str:
        """
        Return basic information about the hospital.

        Returns:
            A string containing the hospital name, address, and phone number.
        """
        return (
            f"Name: {self._name}, "
            f"Address: {self._address}, "
            f"Phone Number: {self._phone}, "
            f"Capacity: {self.get_patient_count()}/{self._capacity}"
        )