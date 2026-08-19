class Person:
    def __init__(self , name:str , age:int,id:str,gender:str,email:str):
        self.name = name
        self.age = age
        self.id = id
        self.gender = gender
        self.email = email

    def view_info(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"ID: {self.id}")
        print(f"Gender: {self.gender}")
        print(f"Email: {self.email}")
    def update_contact_info(self):
        choice = input("""Choose what you want to update:
        1) Name
        2) Age
        3) ID
        4) Gender
        5) Email
        Please enter your choice: """)
        if choice == "1":
         self.name = input("Enter new name: ")
        elif choice == "2":
            self.age = int(input("Enter new age: "))
        elif choice == "3":
            self.id = input("Enter new ID: ")
        elif choice == "4":
            self.gender = input("Enter new gender: ")
        elif choice == "5":
            self.email = input("Enter new email: ")
        else:
         print("Invalid choice!")

    
                 
