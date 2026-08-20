class Hospital:
    """Represent a hospital that manages departments, patients, and staff."""

    def __init__(
        self,
        id: int,
        name: str,
        address: str,
        phone: str,
        capicity: int
    ) -> None:
        """
        Initialize a hospital.

        Args:
            id: The unique identifier of the hospital.
            name: The name of the hospital.
            address: The physical address of the hospital.
            phone: The contact phone number of the hospital.
            capicity: The maximum number of patients the hospital can accommodate.
        """
        self.id = id
        self.departments = []
        self.name = name
        self.address = address
        self.phone = phone
        self.capicity = capicity

    def add_department(self, department: object) -> None:
        """
        Add a department to the hospital.

        Args:
            department: The department object to add.
        """
        self.departments.append(department)

    def remove_department(self, department: object) -> None:
        """
        Remove a department from the hospital.

        Args:
            department: The department object to remove.
        """
        self.departments.remove(department)

    def get_department_count(self) -> int:
        """
        Return the number of departments in the hospital.

        Returns:
            The total number of departments.
        """
        count = 0

        for department in self.departments:
            count += 1

        return count

    def get_patient_count(self, patients: list) -> int:
        """
        Return the number of patients.

        Args:
            patients: A list containing patient objects.

        Returns:
            The total number of patients.
        """
        count = 0

        for patient in patients:
            count += 1

        return count

    def get_staff_count(self, doctors: list) -> int:
        """
        Return the number of staff members.

        Args:
            doctors: A list containing doctor objects.

        Returns:
            The total number of staff members.
        """
        count = 0

        for doctor in doctors:
            count += 1

        return count

    def get_available_capicity(self, patients: list) -> int:
        """
        Calculate the remaining patient capacity of the hospital.

        Args:
            patients: A list containing patient objects.

        Returns:
            The number of available places for additional patients.
        """
        count = self.capicity - self.get_patient_count(patients)

        return count

    def get_info(self) -> str:
        """
        Return basic information about the hospital.

        Returns:
            A string containing the hospital name, address, and phone number.
        """
        return (
            f"Name: {self.name}, "
            f"Address: {self.address}, "
            f"Phone Number: {self.phone}"
        )