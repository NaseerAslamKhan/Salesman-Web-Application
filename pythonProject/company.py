class Company:
    def __init__(self):
        f = open("company.txt", "r")
        self.name = f.readline()
        self.address = f.readline()
        self.phone = f.readline()
        self.email = f.readline()
        self.lowStockLimit = f.readline()
        self.excessStockLimit = f.readline()
        self.tax = f.readline()
        self.discount = f.readline()
        self.shippingFee = f.readline()
        f.close()

    def set(self, name, address, phone, email, low, excess, tax, discount, shippingFee):
        f = open("company.txt", "w")
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.lowStockLimit = low
        self.excessStockLimit = excess
        self.tax = tax
        self.discount = discount
        self.shippingFee = shippingFee
        f.write(name+"\n"+address+"\n"+phone+"\n"+email+"\n"+low+"\n"+excess+"\n"+tax+"\n"+discount+"\n"+shippingFee )
        f.close()