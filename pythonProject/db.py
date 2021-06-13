import pymysql

class DBHandler:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def addUser(self, email, password, emailStatus, accountStatus, firstName, lastName, phone, address, dateOfBirth, gender):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "insert into user (email,password,email_status,account_status,first_name,last_name,phone,address,date_of_birth,gender) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            args = (email, password, emailStatus, accountStatus, firstName, lastName, phone, address, dateOfBirth, gender)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def emailVerified(self, email):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update user set email_status = 'verified' where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def isUserExist(self, email):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select * from user where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        if databaseCursor.rowcount == 0:
            return False
        else:
            return True

    def changePassword(self, email, password):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update user set password = %s where email=%s"
            args = (password, email)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def isLogin(self, email, password):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select * from user where email=%s and binary password=%s"
            args = (email, password)
            databaseCursor.execute(sql, args)
            database.commit()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        if databaseCursor.rowcount == 0:
            return False
        else:
            return True

    def isAccountActive(self, email):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select account_status from user where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        if result[0][0] == "active":
            return True
        else:
            return False

    def changeAccountStatus(self, email):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update user set account_status = case when account_status='inactive' then 'active' when account_status='active' then 'inactive' end where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def getInformation(self, email):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select * from user where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def changeInformation(self, firstName, lastName, phone, address, dateOfBirth, gender, email):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update user set first_name=%s,last_name=%s,phone=%s,address=%s,date_of_birth=%s,gender=%s where email=%s"
            args = (firstName, lastName, phone, address, dateOfBirth, gender, email)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def removeUser(self, email):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "delete from user  where email=%s"
            args = (email)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def addProduct(self, title, image, price, quantity, category, size, status, description):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "insert into product (product_title,product_img,product_price,product_quantity,product_category,product_size,product_status,product_desc) values (%s,%s,%s,%s,%s,%s,%s,%s)"
            args = (title, image, price, quantity, category, size, status, description)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def changeProductStatus(self, productName):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update product set product_status = case when product_status='inactive' then 'active' when product_status='active' then 'inactive' end where product_title=%s"
            args = (productName)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def removeProduct(self, productTitle):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "delete from product  where product_title=%s"
            args = (productTitle)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def getInformationOfProduct(self, productTitle):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select * from product where product_title=%s"
            args = (productTitle)
            databaseCursor.execute(sql, args)
            database.commit()
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def changeInformationOfProduct(self, productImage, productPrice, productQuantity, productCategory, productSize, productDescription, productTitle):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update product set product_img=%s,product_price=%s,product_quantity=%s,product_category=%s,product_size=%s,product_desc=%s where product_title=%s"
            args = (productImage, productPrice, productQuantity, productCategory, productSize, productDescription, productTitle)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def changeOrderStatus(self, email, dateTime):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "update orderdetail set orderdetail_status = case when orderdetail_status='pending' then 'delivered' when orderdetail_status='delivered' then 'pending' end where user_id=(select user_id from firstdatabase.user where email=%s) and orderdetail_datetime=%s"
            args = (email, dateTime)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def report(self, txt):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            databaseCursor.execute(sql)

            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def reportNoOfRows(self, txt):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            databaseCursor.execute(sql)

        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return databaseCursor.rowcount

    def reportOneNoOfRows(self, txt, arg):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            databaseCursor.execute(sql, arg)

        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return databaseCursor.rowcount

    def showTable(self, txt, startDate, lastDate):
        list = []
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            args = (startDate, lastDate)
            databaseCursor.execute(sql, args)

            result = databaseCursor.fetchall()
            for x in result:
                list.append((x[0], x[1], x[2], x[3], x[4], x[5]))
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return list

    def reportWithOneArg(self, txt, arg):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            args = (arg)
            databaseCursor.execute(sql, args)

            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def stockTable(self, txt, arg):
        list = []
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()

            sql = txt
            args = (arg)
            databaseCursor.execute(txt, args)

            result = databaseCursor.fetchall()
            for x in result:
                list.append((x[0], x[1], x[2], x[3], x[4], x[5], x[6]))
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return list

    def showTableZero(self, txt):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            databaseCursor.execute(txt)
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def showTableOne(self, txt, arg):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            databaseCursor.execute(txt, arg)
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def showTableTwo(self, txt, arg1, arg2):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            args = (arg1, arg2)
            databaseCursor.execute(txt, args)
            result = databaseCursor.fetchall()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return result

    def productExistInBag(self, userId, productId):
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "select * from firstdatabase.bag where user_id=%s and product_id=%s"
            args = (userId, productId)
            databaseCursor.execute(sql, args)
            database.commit()
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        if databaseCursor.rowcount == 0:
            return False
        else:
            return True

    def addProductInBag(self, userId, productId):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "insert into firstdatabase.bag (user_id,product_id,bag_quantity) values (%s,%s,1)"
            args = (userId, productId)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def increamentProductInBag(self, userId, productId):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            sql = "UPDATE firstdatabase.bag SET bag_quantity = bag_quantity + 1 where user_id=%s and product_id=%s"
            args = (userId, productId)
            databaseCursor.execute(sql, args)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def removeOne(self, txt, arg):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            databaseCursor.execute(txt, arg)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def changeQuantity(self, txt, arg1, arg2):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            arg = (arg1, arg2)
            databaseCursor.execute(txt, arg)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag

    def three(self, txt, arg1, arg2, arg3):
        flag = False
        database = None
        try:
            database = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            databaseCursor = database.cursor()
            arg = (arg1, arg2, arg3)
            databaseCursor.execute(txt, arg)
            database.commit()
            flag = True
        except Exception as e:
            print("Exception Exist")
            print(e)
        finally:
            if database != None:
                database.close()
        return flag