class Admin:
    def __init__(self):
        f = open("admin.txt", "r")
        self.email = f.readline()
        self.password = f.readline()
        self.first = f.readline()
        self.last = f.readline()
        self.phone = f.readline()
        self.address = f.readline()
        self.dateOfBirth = f.readline()
        self.gender = f.readline()
        f.close()

    def setAdminFile(self, email, password, first, last, phone, address, dateOfBirth, gender):
        f = open("admin.txt", "w")
        self.email = email
        self.password = password
        self.first = first
        self.last = last
        self.phone = phone
        self.address = address
        self.dateOfBirth = dateOfBirth
        self.gender = gender
        f.write(email+"\n"+password+"\n"+first+"\n"+last+"\n"+phone+"\n"+address+"\n"+dateOfBirth+"\n"+gender)
        f.close()