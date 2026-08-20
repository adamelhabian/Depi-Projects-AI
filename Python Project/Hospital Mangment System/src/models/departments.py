


class Department:

    def __init__(self,id:int,
                name:str,
                location:str,
                capacity:int=50):
        self.patients=[]
        self.staff=[]
        self.id=id
        self.name=name
        self.location=location
        self.capacity=capacity

    def add_patient(self):
        pass

    def remove_patient(self):
        pass

    def add_staff(self):
        pass

    def remove_staff(self):
        pass

    def get_patient_count(self):
        return len(self.patients)

    def get_staff_count(self):
        return len(self.staff)

    def get_available_capacity(self):
        return self.capacity-self.get_patient_count()

    def get_info(self):
        return f"""
        Departent Information:
        Name: {self.name}
        ID: {self.id}
        Location: {self.location}
        It's Capacity: {self.capacity} Patient
        Num of Patients on it Now : {self.get_patient_count()}
        Available Capacity : {self.get_available_capacity()} Patients
        Num of Stuff on it {self.get_staff_count()} Stuff
        """


        