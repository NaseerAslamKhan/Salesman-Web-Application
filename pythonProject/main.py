from flask import Flask, render_template, request, url_for, session, redirect, make_response, jsonify
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from company import Company
from db import DBHandler
from admin import Admin
import pymysql
import pdfkit
import math
import os

app = Flask(__name__)
PRODUCT_FOLDER = os.path.join('static', 'product_photo')
app.secret_key = "hello"
app.config.from_pyfile('config.cfg')
s = URLSafeTimedSerializer('Thisisasecret!')
senderEmail: str = app.config['MAIL_USERNAME']
db = DBHandler(app.config['HOST'], app.config['USER'], app.config['PASSWORD'], app.config['DATABASE'])
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def startingPoint():
    return index()


@app.route('/login-register', methods=['GET', 'POST'])
def loginRegister():
    company = Company()
    response = make_response(render_template('login-register.html', not_login="no", company=company))
    return response


@app.route('/sign-in', methods=['POST'])
def sign_in():
    email = request.form["email"]
    password = request.form["password"]

    admin = Admin()
    company = Company()
    adminEmail = admin.email.rstrip("\n")
    adminPassword = admin.password.rstrip("\n")

    if email == adminEmail and password == adminPassword:
        return dashboard()

    if email != adminEmail:
        txt = "select * from user where email=%s"
        rowCount = db.reportOneNoOfRows(txt, email)
        if rowCount > 0:
            if db.isAccountActive(email) == False:
                return render_template('login-register.html', not_login="no", inactive_msg= "Your account is inactive. Contact your administrator to activate it.", company=company)

    if db.isLogin(email, password) == True:
        txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2  FROM firstdatabase.product where product_category LIKE 'MEN%' and product_status='active' order by product_id desc Limit 0,6"
        menLatest = db.showTableZero(txt)

        txt = "SELECT order.product_id,product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'MEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
        menBestSale = db.showTableZero(txt)

        txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'WOMEN%' and product_status='active' order by product_id desc Limit 0,6"
        womenLatest = db.showTableZero(txt)

        txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'WOMEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
        womenBestSale = db.showTableZero(txt)

        txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'KIDS%' and product_status='active' order by product_id desc Limit 0,6"
        kidsLatest = db.showTableZero(txt)

        txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'KIDS%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
        kidsBestSale = db.showTableZero(txt)

        login_email = request.cookies.get("email")

        if login_email is None or login_email == "":
            if email != "" and password != "":
                response = make_response(
                    render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale,
                                    womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest,
                                    kidsBestSale=kidsBestSale, login_email=email))
                response.set_cookie('email', email)
                return response

            response = make_response(
                render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale,
                                womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest,
                                kidsBestSale=kidsBestSale, not_login="not"))
        else:
            response = make_response(
                render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale,
                                womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest,
                                kidsBestSale=kidsBestSale, login_email=login_email))

        response.set_cookie('email', email)

    else:
        return render_template('login-register.html', company=company, not_login="not", inactive_msg="Invalid Login or Password")


@app.route('/sign-up', methods=['POST'])
def sign_up():
    company = Company()
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        firstName = request.form["first-name"]
        lastName = request.form["last-name"]
        phone = request.form["phone"]
        address = request.form["address"]
        dateOfBirth = request.form["date-of-birth"]
        gender = request.form["gender"]

        if db.isUserExist(email) == True:
            msg = "An account is already registered with this email address"
            return render_template('login-register.html', company=company, not_login="no", inactive_msg=msg)

        db.addUser(email, password, "unverified", "active", firstName, lastName, phone, address, dateOfBirth, gender)
        token = s.dumps(email, salt='email-confirm')
        msg = Message('Email Confirmation', sender=senderEmail, recipients=[email])
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'To complete your sign up, please verify your email: <a href="{}">Verify Email</a>.<br><br><br>This link is valid for only 5 min'.format(link)
        mail.send(msg)

        msg = "Please Verify your Email Address. We have sent the verification mail to {}. If you cannot find the email verification mail in the index folder. Please check spam/junk folder".format(email)
        return render_template('login-register.html', company=company, not_login="no", info_msg=msg)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    company = Company()
    if request.method == 'GET':
        return render_template('forgot-password.html', company=company, not_login="not")

    email = request.form["email"]

    if db.isUserExist(email) == False:
        return render_template('forgot-password.html', company=company, not_login="not", error_msg="No Account associated with this email address")

    token = s.dumps(email, salt='reset-passwords')
    msg = Message('Reset Password', sender=senderEmail, recipients=[email])
    link = url_for('reset_password', token=token, _external=True)
    msg.body = "We are sending you this email because you requested a password reset. Click on this link to create a new password:" \
               "<br><br><a href='{}'>Set a new password</a>.<br><br>Link is valid for only 5 min. If you didn't request a password " \
               "reset, you can ignore this email.".format(link)
    mail.send(msg)

    return render_template('forgot-password.html', company=company, not_login="not", success_msg="We have emailed your password reset link")


@app.route('/reset-password', methods=['POST'])
def resetPassword():
    company = Company()
    password = request.form["password"]
    email = session.pop('email', None)
    db.changePassword(email, password)
    msg = "Your Password Changed Successfully"
    return render_template('login-register.html', password_msg=msg, company=company, not_login="no")


@app.route('/confirm_email/<token>')
def confirm_email(token):
    company = Company()
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
    except SignatureExpired:
        msg = "The email verification link is expired"
        return render_template('login-register.html', company=company, error_msg=msg ,not_login="no")
    db.emailVerified(email)
    msg = "Thank you for your support, we have successfully verified your email"
    return render_template('login-register.html', company=company, email_msg=msg ,not_login="no")


@app.route('/reset_password/<token>')
def reset_password(token):
    company = Company()
    try:
        email = s.loads(token, salt='reset-passwords', max_age=300)
    except SignatureExpired:
        msg = "The reset password link is expired"
        return render_template('login-register.html',company=company,not_login="no", error_msg=msg)
    session['email'] = email
    return render_template('reset-password.html', company=company, not_login="not")


@app.route('/logout')
def logout():
    company = Company()
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2  FROM firstdatabase.product where product_category LIKE 'MEN%' and product_status='active' order by product_id desc Limit 0,6"
    menLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'MEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    menBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'WOMEN%' and product_status='active' order by product_id desc Limit 0,6"
    womenLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'WOMEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    womenBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'KIDS%' and product_status='active' order by product_id desc Limit 0,6"
    kidsLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'KIDS%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    kidsBestSale = db.showTableZero(txt)

    response = make_response(
        render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale,
                        womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest,
                        kidsBestSale=kidsBestSale, not_login="not"))

    response.set_cookie('email', '')
    return response


@app.route('/delete', methods=['POST'])
def delete():
    email = request.cookies.get("email")
    token = s.dumps(email, salt='delete-confirmations')
    msg = Message('Delete Confirmation', sender=senderEmail, recipients=[email])
    link = url_for('delete_confirmation', token=token, _external=True)
    msg.body = "We've received a request to permanently delete your account. Once account is deleted, there will be no option to get your account back." \
               "<br><br>If you don't want to delete your account, please ignore this message and your data won't be lost.<br><br>If you still" \
               " wish to permanently delete your account, and lose all of your data, click the link below:" \
               "<br><br><a href='{}'>Delete Account</a>.<br><br>Link is valid for only 5 min.".format(link)
    mail.send(msg)

    msg = "We have email your delete confirmation link"

    response = make_response(render_template('login-register.html', company=company, not_login="no", info_msg=msg))
    response.set_cookie('email', '')
    return response


@app.route('/delete_confirmation/<token>')
def delete_confirmation(token):
    company = Company()
    try:
        email = s.loads(token, salt='delete-confirmations', max_age=300)
    except SignatureExpired:
        msg = "The delete account link is expired"
        return render_template('login-register.html',company=company,not_login="no", error_msg=msg)
    session['email'] = email
    if db.removeUser(email) == True:
        msg = "Your account deleted successfully"
        return render_template('login-register.html',company=company,not_login="no", delete_msg=msg)
    else:
        msg = "We are unable to delete your account"
        return render_template('login-register.html', company=company, not_login="no", inactive_msg=msg)


@app.route('/changePassword', methods=['POST'])
def changePassword():
    email = request.cookies.get("email")
    token = s.dumps(email, salt='reset-passwords')
    msg = Message('Reset Password', sender=senderEmail, recipients=[email])
    link = url_for('reset_password', token=token, _external=True)
    msg.body = "We are sending you this email because you requested a password reset. Click on this link to create a new password:" \
               "<br><br><a href='{}'>Set a new password</a>.<br><br>Link is valid for only 5 min. If you didn't request a password " \
               "reset, you can ignore this email.".format(link)
    mail.send(msg)

    msg = "We have emailed your reset password link"

    response = make_response(render_template('login-register.html', company=company, not_login="no", info_msg=msg))
    response.set_cookie('email', '')
    return response


@app.route('/verifyEmail', methods=['POST'])
def verifyEmail():
    company = Company()
    email = request.cookies.get("email")
    token = s.dumps(email, salt='email-confirm')
    msg = Message('Email Confirmation', sender=senderEmail, recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = 'To complete your sign up, please verify your email: <a href="{}">Verify Email</a>.<br><br><br>This link is valid for only 5 min'.format(
        link)
    mail.send(msg)

    msg = "Please Verify your Email Address. We have sent the verification mail to {}. If you cannot find the email verification mail in the index folder. Please check spam/junk folder".format(email)

    response = make_response(render_template('login-register.html',company=company,not_login="no", info_msg=msg))
    response.set_cookie('email', '')
    return response


@app.route('/profile')
def profile():
    admin = Admin()
    return render_template('profile.html', email=admin.email, password=admin.password,
                           firstName=admin.first,
                           lastName=admin.last, phone=admin.phone, address=admin.address,
                           dateOfBirth=admin.dateOfBirth, gender=admin.gender, admin_email=admin.email)


@app.route('/user-information', methods=['GET','POST'])
def userInformation():
    admin = Admin()
    if request.method == 'GET':
        txt = "SELECT @ab:=@ab+1 as SrNo, email,first_name,last_name,phone,gender,email_status,account_status FROM user, (SELECT @ab:= 0) AS ab"
        table = db.showTableZero(txt)
        response = make_response(render_template('user-information.html', usersList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
        return response

    email = request.form["email"]
    db.changeAccountStatus(email)
    txt = "SELECT @ab:=@ab+1 as SrNo, email,first_name,last_name,phone,gender,email_status,account_status FROM user, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('user-information.html', usersList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/product')
def product():
    admin = Admin()
    txt = "SELECT @ab:=@ab+1 as SrNo, product_title,product_img,product_price,product_quantity,product_category,product_size,product_status FROM product, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('product.html', productsList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/product-add')
def productAdd():
    admin = Admin()
    response = make_response(render_template('product-add.html',admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/productAddForm', methods=['POST'])
def productAddForm():
    admin = Admin()
    title = request.form["product-title"]

    price = request.form["product-price"]
    quantity = request.form["product-quantity"]
    category = request.form["product-category"]
    size = request.form["product-size"]
    description = request.form["product-desc"]

    file_1 = request.files['product-img-1']
    filename = secure_filename(file_1.filename)
    file_1.save(os.path.join('static/product_photo/', filename))

    file_2 = request.files['product-img-2']
    filename = secure_filename(file_2.filename)
    file_2.save(os.path.join('static/product_photo/', filename))

    image_path = file_1.filename + ':' + file_2.filename

    db.addProduct(title, image_path, price, quantity, category, size, "active", description)
    txt = "SELECT @ab:=@ab+1 as SrNo, product_title,product_img,product_price,product_quantity,product_category,product_size,product_status FROM product, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('product.html', productsList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/productStatusForm', methods=['POST'])
def productStatusForm():
    admin = Admin()
    productTitle = request.form["product-title"]
    db.changeProductStatus(productTitle)
    txt = "SELECT @ab:=@ab+1 as SrNo, product_title,product_img,product_price,product_quantity,product_category,product_size,product_status FROM product, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('product.html', productsList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/productDeleteForm', methods=['POST'])
def productDeleteForm():
    admin = Admin()
    productTitle = request.form["product-title"]
    db.removeProduct(productTitle)
    txt = "SELECT @ab:=@ab+1 as SrNo, product_title,product_img,product_price,product_quantity,product_category,product_size,product_status FROM product, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('product.html', productsList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/product-edit', methods=['POST'])
def productEdit():
    admin = Admin()
    productTitle = request.form["product-title"]
    txt = "select product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size, product_status, product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 from product where product_title=%s"
    result = db.showTableOne(txt, productTitle)

    return render_template('product-edit.html', productTitle=result[0][1], productImage1=result[0][2], productPrice=result[0][3],
                           productQuantity=result[0][4],
                           productCategory=result[0][5], productSize=result[0][6], productDescription=result[0][8],
                           productImage2=result[0][9] ,admin_email=admin.email,firstName=admin.first,lastName=admin.last)


@app.route('/productEditForm', methods=['POST'])
def productEditForm():
    admin = Admin()
    productTitle = request.form["product-title"]
    productImage = request.form["product-imgs"]
    productPrice = request.form["product-price"]
    productQuantity = request.form["product-quantity"]
    productCategory = request.form["product-category"]
    productSize = request.form["product-size"]
    productDescription = request.form["product-desc"]

    file_1 = request.files['product-img-1']
    file_2 = request.files['product-img-2']
    file_1.seek(0, os.SEEK_END)
    file_2.seek(0, os.SEEK_END)
    if file_1.tell() != 0 and file_2.tell() != 0:
        filename = secure_filename(file_1.filename)
        file_1.save(os.path.join('static/product_photo/', filename))

        filename = secure_filename(file_2.filename)
        file_2.save(os.path.join('static/product_photo/', filename))

        image_path = file_1.filename + ':' + file_2.filename
    else:
        txt = "SELECT * FROM product where product_title=%s"
        previous_image = db.showTableOne(txt, productTitle)
        image_path = previous_image[0][2]

    db.changeInformationOfProduct(image_path, productPrice, productQuantity, productCategory, productSize, productDescription, productTitle)
    txt = "SELECT @ab:=@ab+1 as SrNo, product_title,product_img,product_price,product_quantity,product_category,product_size,product_status FROM product, (SELECT @ab:= 0) AS ab"
    table = db.showTableZero(txt)
    response = make_response(render_template('product.html', productsList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/order')
def order():
    admin = Admin()
    txt = "SELECT @ab:=@ab+1 as SrNo,concat(user.first_name,' ',user.last_name) as Name,user.email,orderdetail_datetime,orderdetail_status FROM firstdatabase.orderdetail,firstdatabase.order,firstdatabase.user, (SELECT @ab:= 0) AS ab where user.user_id=orderdetail.user_id and order.order_id=orderdetail.order_id group by orderdetail_datetime order by orderdetail_datetime desc"
    table = db.showTableZero(txt)
    response = make_response(render_template('order.html', ordersList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/orderStatusForm', methods=['POST'])
def orderStatusForm():
    admin = Admin()
    email = request.form["user-email"]
    dateTime = request.form["orderdetail-datetime"]
    db.changeOrderStatus(email, dateTime)
    txt = "SELECT @ab:=@ab+1 as SrNo,concat(user.first_name,' ',user.last_name) as Name,user.email,orderdetail_datetime,orderdetail_status FROM firstdatabase.orderdetail,firstdatabase.order,firstdatabase.user, (SELECT @ab:= 0) AS ab where user.user_id=orderdetail.user_id and order.order_id=orderdetail.order_id group by orderdetail_datetime order by orderdetail_datetime desc"
    table = db.showTableZero(txt)
    response = make_response(render_template('order.html', ordersList=table,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/viewOrderForm', methods=['POST'])
def viewOrderForm():
    admin = Admin()
    email = request.form["user-email"]
    dateTime = request.form["orderdetail-datetime"]
    txt = "SELECT @ab:=@ab+1 as SrNo,product.product_id,product.product_title,product.product_size,order.order_quantity,product.product_price,order.order_quantity*product.product_price as TOTAL FROM firstdatabase.orderdetail,firstdatabase.user, firstdatabase.order,firstdatabase.product, (SELECT @ab:= 0) AS ab where orderdetail.user_id=user.user_id and order.order_id=orderdetail.order_id and order.product_id=product.product_id and user.email=%s and orderdetail_datetime=%s"
    table = db.showTableTwo(txt, email, dateTime)
    txt = "SELECT sum(order.order_quantity*product.product_price) FROM firstdatabase.orderdetail,firstdatabase.user, firstdatabase.order,firstdatabase.product where orderdetail.user_id=user.user_id and order.order_id=orderdetail.order_id and order.product_id=product.product_id and user.email=%s and orderdetail_datetime=%s"
    totalAmount = db.showTableTwo(txt, email, dateTime)
    response = make_response(render_template('order-detail.html', orderDetailList=table,totalAmount=totalAmount[0][0],admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/dashboard', methods=['GET'])
def dashboard():
    admin=Admin()
    company = Company()
    totalProducts=db.report("select count(*) from product")
    activeProducts=db.report("select count(*) from product where product_status='active'")
    inactiveProducts = db.report("select count(*) from product where product_status='inactive'")

    totalUsers = db.report("select count(*) from user")
    activeUsers = db.report("select count(*) from user where account_status='active'")
    inactiveUsers = db.report("select count(*) from user where account_status='inactive'")

    totalOrders = db.reportNoOfRows("SELECT count(*) FROM firstdatabase.orderdetail,firstdatabase.order,firstdatabase.user where user.user_id=orderdetail.user_id and order.order_id=orderdetail.order_id group by orderdetail_datetime")
    pendingOrders = db.reportNoOfRows("SELECT count(*) FROM firstdatabase.orderdetail,firstdatabase.order,firstdatabase.user where user.user_id=orderdetail.user_id and order.order_id=orderdetail.order_id and orderdetail_status='pending' group by orderdetail_datetime")
    deliveredOrders = db.reportNoOfRows("SELECT count(*) FROM firstdatabase.orderdetail,firstdatabase.order,firstdatabase.user where user.user_id=orderdetail.user_id and order.order_id=orderdetail.order_id and orderdetail_status='delivered' group by orderdetail_datetime")

    outOfStockProducts = db.reportWithOneArg("SELECT count(*) FROM product where product_quantity=%s", 0)
    lowerStockProducts = db.reportWithOneArg("SELECT count(*) FROM product where product_quantity<=%s", company.lowStockLimit)
    excessStockProducts = db.reportWithOneArg("SELECT count(*) FROM product where product_quantity>=%s", company.excessStockLimit)

    response = make_response(render_template('dashboard.html', totalProducts=totalProducts[0][0], activeProducts=activeProducts[0][0],
                                             inactiveProducts=inactiveProducts[0][0], totalUsers=totalUsers[0][0],
                                             activeUsers=activeUsers[0][0], inactiveUsers=inactiveUsers[0][0], totalOrders=totalOrders,
                                              pendingOrders=pendingOrders, deliveredOrders=deliveredOrders, outOfStockProducts=outOfStockProducts[0][0],
                                             lowerStockProducts=lowerStockProducts[0][0], excessStockProducts=excessStockProducts[0][0],admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/report', methods=['GET'])
def report():
    admin = Admin()
    dateTable = []
    amountTable = []
    totalAmountTable = []

    for x in range(10):
        date = datetime.today() - timedelta(days=x)
        date = date.strftime("%Y-%m-%d")
        dateTable.append(date)
        txt = "SELECT sum(order.order_quantity*product.product_price) FROM firstdatabase.orderdetail,firstdatabase.user, firstdatabase.order,firstdatabase.product where orderdetail.user_id=user.user_id and order.order_id=orderdetail.order_id and order.product_id=product.product_id and orderdetail_datetime LIKE '%{}%'".format(date)
        amount = db.showTableZero(txt)
        amountTable.append(amount)

    for x in range(10):
        if (amountTable[x][0][0]) == 'None':
            totalAmountTable.append(0)
        else:
            totalAmountTable.append((amountTable[x][0][0]))

    for x in range(10):
        if totalAmountTable[x] == None:
            totalAmountTable[x] = '0'

    response = make_response(render_template('report.html',admin_email=admin.email,firstName=admin.first,lastName=admin.last, totalAmount=totalAmountTable, dateTable=dateTable))
    return response


@app.route('/itemSaleSummary', methods=['GET','POST'])
def itemSaleSummary():
    admin = Admin()
    if request.method == 'GET':
        startDate = datetime.today() - timedelta(days=10)
        lastDate = datetime.today() - timedelta(days=0)
        itemSaleSummary = db.showTable(
            "SELECT order.product_id,product_title, SUM(order_quantity) as TotalQuantity,product_price,SUM(order_quantity)*product_price,product_quantity as stock FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and orderdetail_datetime>=%s and orderdetail_datetime<=%s GROUP BY order.product_id ORDER BY TotalQuantity DESC",
            startDate, lastDate)
        return render_template('itemSaleSummary.html', itemSaleSummary=itemSaleSummary, reportType="Top sold items by quantity", date="Last 10 days",admin_email=admin.email,firstName=admin.first,lastName=admin.last)

    date = request.form["date"]
    if date == 'Last 10 days':
        startDate = datetime.today() - timedelta(days=10)
        lastDate = datetime.today() - timedelta(days=0)
    elif date == 'Last 30 days':
        startDate = datetime.today() - timedelta(days=30)
        lastDate = datetime.today() - timedelta(days=0)
    elif date == 'Past 3 months':
        startDate = datetime.today() - timedelta(days=91)
        lastDate = datetime.today() - timedelta(days=0)
    elif date == 'Past 6 months':
        startDate = datetime.today() - timedelta(days=182)
        lastDate = datetime.today() - timedelta(days=0)
    elif date == 'Past 12 months':
        startDate = datetime.today() - timedelta(days=364)
        lastDate = datetime.today() - timedelta(days=0)
    elif date == 'Overall':
        startDate = '2000-1-1'
        lastDate = datetime.today() - timedelta(days=0)

    saleSummary = request.form["saleSummary"]

    if saleSummary == 'Top sold items by quantity':
        itemSaleSummary=db.showTable("SELECT order.product_id,product_title, SUM(order_quantity) as TotalQuantity,product_price,SUM(order_quantity)*product_price,product_quantity as stock FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and orderdetail_datetime>=%s and orderdetail_datetime<=%s GROUP BY order.product_id ORDER BY TotalQuantity DESC", startDate, lastDate)
    elif saleSummary == 'Top sold items by amount':
        itemSaleSummary=db.showTable("SELECT order.product_id,product_title, SUM(order_quantity) as TotalQuantity,product_price,SUM(order_quantity)*product_price as Amount,product_quantity as stock FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and orderdetail_datetime>=%s and orderdetail_datetime<=%s GROUP BY order.product_id ORDER BY Amount DESC", startDate, lastDate)
    elif saleSummary == 'Low sold items by quantity':
        itemSaleSummary=db.showTable("SELECT order.product_id,product_title, SUM(order_quantity) as TotalQuantity,product_price,SUM(order_quantity)*product_price,product_quantity as stock FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and orderdetail_datetime>=%s and orderdetail_datetime<=%s GROUP BY order.product_id ORDER BY TotalQuantity ASC", startDate, lastDate)
    else:
        itemSaleSummary=db.showTable("SELECT order.product_id,product_title, SUM(order_quantity) as TotalQuantity,product_price,SUM(order_quantity)*product_price as Amount,product_quantity as stock FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and orderdetail_datetime>=%s and orderdetail_datetime<=%s GROUP BY order.product_id ORDER BY Amount ASC", startDate, lastDate)

    response = make_response(render_template('itemSaleSummary.html', itemSaleSummary=itemSaleSummary, reportType=saleSummary, date=date,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    admin = Admin()
    if request.method == 'GET':
        table = db.stockTable("SELECT @ab:=@ab+1 as SrNo, product_id,product_title,product_size,product_price,product_quantity,product_price*product_quantity FROM product, (SELECT @ab:= 0) AS ab where product_quantity>=%s", 0)
        stockValue = db.report("SELECT sum(product_price*product_quantity) FROM product")
        response = make_response(render_template('stock.html', stockList=table, stockValue=stockValue[0][0], stockType="Stock Value",admin_email=admin.email,firstName=admin.first,lastName=admin.last))
        return response

    company = Company()
    stockType = request.form["stockType"]

    if stockType == "Stock Value":
        table = db.stockTable("SELECT @ab:=@ab+1 as SrNo, product_id,product_title,product_size,product_price,product_quantity,product_price*product_quantity FROM product, (SELECT @ab:= 0) AS ab where product_quantity>=%s",0)
        stockValue = db.report("SELECT sum(product_price*product_quantity) FROM product")
        response = make_response(render_template('stock.html', stockList=table, stockValue=stockValue[0][0], stockType="Stock Value",admin_email=admin.email,firstName=admin.first,lastName=admin.last))
        return response
    elif stockType == "Out of Stock Items":
        table = db.stockTable("SELECT @ab:=@ab+1 as SrNo, product_id,product_title,product_size,product_price,product_quantity,product_price*product_quantity FROM product, (SELECT @ab:= 0) AS ab where product_quantity=%s",0)
    elif stockType == "Lower Stock Items":
        table = db.stockTable("SELECT @ab:=@ab+1 as SrNo, product_id,product_title,product_size,product_price,product_quantity,product_price*product_quantity FROM product, (SELECT @ab:= 0) AS ab where product_quantity<=%s",company.lowStockLimit)
    else:
        table = db.stockTable("SELECT @ab:=@ab+1 as SrNo, product_id,product_title,product_size,product_price,product_quantity,product_price*product_quantity FROM product, (SELECT @ab:= 0) AS ab where product_quantity>=%s",company.excessStockLimit)

    response = make_response(render_template('stock.html', stockList=table, stockType=stockType,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/company', methods=['GET', 'POST'])
def company():
    admin = Admin()
    company = Company()
    if request.method == 'GET':
        response = make_response(render_template('company.html',companyName=company.name,companyAddress=company.address,companyPhone=company.phone,
                                             companyEmail=company.email,companyLow=company.lowStockLimit,companyExcess=company.excessStockLimit,
                                             companyTax=company.tax,companyDiscount=company.discount,companyShipping=company.shippingFee,
                                                 admin_email=admin.email,firstName=admin.first,lastName=admin.last))
        return response

    name = request.form["name"]
    address = request.form["address"]
    phone = request.form["phone"]
    email = request.form["email"]
    low = request.form["low-stock"]
    excess = request.form["excess-stock"]
    tax = request.form["tax"]
    discount = request.form["discount"]
    shipping = request.form["shipping"]

    company.set(name,address,phone,email,low,excess,tax,discount,shipping)
    response = make_response(render_template('company.html', companyName=company.name, companyAddress=company.address,
                                             companyPhone=company.phone,companyEmail=company.email,
                                             companyLow=company.lowStockLimit,companyExcess=company.excessStockLimit,
                                             companyTax=company.tax, companyDiscount=company.discount,
                                             companyShipping=company.shippingFee,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route('/admin-setting', methods=['GET','POST'])
def adminSetting():
    admin = Admin()
    if request.method == 'GET':
        response = make_response(render_template('admin-setting.html',adminEmail=admin.email,adminPassword=admin.password,adminFirst=admin.first,
                                             adminLast=admin.last,adminPhone=admin.phone,adminAddress=admin.address,
                                             adminDateOfBirth=admin.dateOfBirth,
                                                 adminGender=admin.gender,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
        return response

    email = request.form["email"]
    password = request.form["password"]
    first = request.form["first-name"]
    last = request.form["last-name"]
    phone = request.form["phone"]
    address = request.form["address"]
    dateOfBirth = request.form["date-of-birth"]
    gender = request.form["gender"]

    admin.setAdminFile(email,password,first,last,phone,address,dateOfBirth,gender)
    response = make_response(
        render_template('admin-setting.html', adminEmail=admin.email, adminPassword=admin.password, adminFirst=admin.first,
                        adminLast=admin.last, adminPhone=admin.phone, adminAddress=admin.address,
                        adminDateOfBirth=admin.dateOfBirth, adminGender=admin.gender,admin_email=admin.email,firstName=admin.first,lastName=admin.last))
    return response


@app.route("/live-search-user", methods=['POST'])
def liveSearchUser():
    searchbox = request.form.get("text")
    database = pymysql.connect(host=app.config['HOST'], user=app.config['USER'], password=app.config['PASSWORD'], database=app.config['DATABASE'])
    cursor = database.cursor()
    query = "SELECT @ab:=@ab+1 as SrNo, email,first_name,last_name,phone,gender,email_status,account_status FROM user, (SELECT @ab:= 0) AS ab  where email LIKE '%{}%' or first_name LIKE '%{}%' or last_name LIKE '%{}%' or CONCAT(first_name,' ', last_name) LIKE '%{}%' or phone LIKE '%{}%' or gender LIKE '%{}%' or email_status LIKE '%{}%' or account_status LIKE '%{}%'".format(searchbox, searchbox, searchbox, searchbox, searchbox, searchbox, searchbox, searchbox)
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/place-order', methods=['POST'])
def placeOrder():
    login_email = request.cookies.get("email")
    productId = request.form["product-id"]
    userId = db.getInformation(login_email)
    userId = userId[0][0]

    if db.productExistInBag(userId,productId) == True:
        db.increamentProductInBag(userId, productId)
    else:
        db.addProductInBag(userId, productId)

    return index()


@app.route("/user-setting", methods=['GET', 'POST'])
def userSetting():
    company = Company()
    login_email = request.cookies.get("email")
    result = db.getInformation(login_email)

    if request.method == 'GET':
        return render_template('user-setting.html',company=company, login_email=login_email,result=result)

    firstName = request.form["first-name"]
    lastName = request.form["last-name"]
    phone = request.form["phone"]
    address = request.form["address"]
    dateOfBirth = request.form["date-of-birth"]
    gender = request.form["gender"]

    db.changeInformation(firstName, lastName, phone, address, dateOfBirth, gender, login_email)
    result = db.getInformation(login_email)

    return render_template('user-setting.html', company=company, login_email=login_email, result=result, success_msg="Your Profile Info Changed Successfully")


@app.route('/user-profile')
def userProfile():
    company = Company()
    login_email = request.cookies.get("email")
    result = db.getInformation(login_email)
    return render_template('user-profile.html', company=company,login_email=login_email, result=result)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    company = Company()
    login_email = request.cookies.get("email")

    if request.method == 'GET':
        if login_email == "":
            response = make_response(render_template('contact.html', company=company, not_login="not login"))
        else:
            response = make_response(render_template('contact.html', company=company, login_email=login_email))
        return response

    email = request.form["email"]
    name = request.form["name"]
    message = request.form["message"]



    msg = Message('Inquiry Message', sender=senderEmail, recipients=[email])
    msg.body = 'Email: "{}"<br>Name: "{}"<br>"{}"'.format(email, name, message)
    mail.send(msg)

    if login_email == "":
        response = make_response(render_template('contact.html', company=company, not_login="not login"))
    else:
        response = make_response(render_template('contact.html', company=company, login_email=login_email))
    return response


@app.route('/login-register-cart-view', methods=['GET', 'POST'])
def login_register_cart_view():
    company = Company()
    msg = "You are not logged in. To view your cart first login your account"
    response = make_response(render_template('login-register.html', msg=msg, company=company, not_login="no"))
    return response


@app.route('/login-register-add-item', methods=['GET', 'POST'])
def login_register_add_item():
    company = Company()
    msg = "You are not logged in. To add item in cart first login your account"
    response = make_response(render_template('login-register.html', msg=msg, company=company, not_login="no"))
    return response


@app.route('/men', methods=['GET', 'POST'])
def men():
    company = Company()
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='MEN CASUAL SHIRTS' and product_status='active' order by product_id desc"
    men_casual_shirts = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='MEN CASUAL T-SHIRTS' and product_status='active' order by product_id desc"
    men_casual_t_shirts = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='MEN CASUAL PANTS' and product_status='active' order by product_id desc"
    men_casual_pants = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='MEN FORMAL SHALWAR KAMEEZ' and product_status='active' order by product_id desc"
    men_formal_shalwar_kameez = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='MEN FORMAL PANT COAT' and product_status='active' order by product_id desc"
    men_formal_pant_coat = db.showTableZero(txt)

    login_email = request.cookies.get("email")

    if login_email is None or login_email == "":
        response = make_response(render_template('men.html', company=company, men_casual_shirts=men_casual_shirts, men_casual_t_shirts=men_casual_t_shirts,men_casual_pants=men_casual_pants, men_formal_shalwar_kameez=men_formal_shalwar_kameez, men_formal_pant_coat=men_formal_pant_coat, not_login="not"))
    else:
        response = make_response(render_template('men.html', company=company, men_casual_shirts=men_casual_shirts,men_casual_t_shirts=men_casual_t_shirts,men_casual_pants=men_casual_pants,men_formal_shalwar_kameez=men_formal_shalwar_kameez,men_formal_pant_coat=men_formal_pant_coat, login_email=login_email))

    return response


@app.route('/women', methods=['GET', 'POST'])
def women():
    company = Company()
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='WOMEN SHALWAR KAMEEZ TWO PIECE' and product_status='active' order by product_id desc"
    women_shalwar_kameez_two = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='WOMEN SHALWAR KAMEEZ THREE PIECE' and product_status='active' order by product_id desc"
    women_shalwar_kameez_three = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='WOMEN ABAYA' and product_status='active' order by product_id desc"
    women_abaya = db.showTableZero(txt)

    login_email = request.cookies.get("email")

    if login_email is None or login_email == "":
        response = make_response(render_template('women.html', company=company, women_shalwar_kameez_two=women_shalwar_kameez_two, women_shalwar_kameez_three=women_shalwar_kameez_three, women_abaya=women_abaya, not_login="not"))
    else:
        response = make_response(render_template('women.html', company=company, women_shalwar_kameez_two=women_shalwar_kameez_two, women_shalwar_kameez_three=women_shalwar_kameez_three, women_abaya=women_abaya, login_email=login_email))

    return response


@app.route('/kids', methods=['GET', 'POST'])
def kids():
    company = Company()
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='KIDS BOYS SHIRTS' and product_status='active' order by product_id desc"
    kids_boys_shirts = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='KIDS BOYS PANTS' and product_status='active' order by product_id desc"
    kids_boys_pants = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='KIDS BOYS KURTA & PAJAMA' and product_status='active' order by product_id desc"
    kids_boys_kurta_pajama = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='KIDS GIRLS KURTI' and product_status='active' order by product_id desc"
    kids_girls_kurti = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category='KIDS GIRLS JEANS' and product_status='active' order by product_id desc"
    kids_girls_jeans = db.showTableZero(txt)

    login_email = request.cookies.get("email")

    if login_email is None or login_email == "":
        response = make_response(render_template('kids.html', company=company, kids_boys_shirts=kids_boys_shirts,kids_boys_pants=kids_boys_pants, kids_boys_kurta_pajama=kids_boys_kurta_pajama,kids_girls_kurti=kids_girls_kurti,kids_girls_jeans=kids_girls_jeans,not_login="not"))
    else:
        response = make_response(render_template('kids.html', company=company, kids_boys_shirts=kids_boys_shirts,kids_boys_pants=kids_boys_pants, kids_boys_kurta_pajama=kids_boys_kurta_pajama,kids_girls_kurti=kids_girls_kurti,kids_girls_jeans=kids_girls_jeans,login_email=login_email))

    return response


@app.route('/index', methods=['GET', 'POST'])
def index():
    company = Company()
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2  FROM firstdatabase.product where product_category LIKE 'MEN%' and product_status='active' order by product_id desc Limit 0,6"
    menLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'MEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    menBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'WOMEN%' and product_status='active' order by product_id desc Limit 0,6"
    womenLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'WOMEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    womenBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'KIDS%' and product_status='active' order by product_id desc Limit 0,6"
    kidsLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'KIDS%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    kidsBestSale = db.showTableZero(txt)

    login_email = request.cookies.get("email")

    if login_email is None or login_email == "":
        response = make_response(render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale, womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest, kidsBestSale=kidsBestSale, not_login="not"))
    else:
        response = make_response(render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale, womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest, kidsBestSale=kidsBestSale, login_email=login_email))
    return response


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    company = Company()
    login_email = request.cookies.get("email")
    userId = db.getInformation(login_email)
    userId = userId[0][0]
    if request.method == 'GET':
        txt = "SELECT @ab:=@ab+1 as SrNo,bag_id,user_id,bag.product_id,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1,product_title,product_size,product_price,product_quantity,bag_quantity,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
        table = db.showTableOne(txt, userId)

        txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
        totalAmount = db.showTableOne(txt, userId)

        txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
        noOfQty = db.showTableOne(txt, userId)
        if noOfQty[0][0] is None:
            response = make_response(
                render_template('cart.html', list=table, company=company, totalAmount=0,
                                shipping=0, tax=0, discount=0, subtotal=0, login_email=login_email))
            return response
        shipping = (int(company.shippingFee) * int(noOfQty[0][0]))

        tax = math.floor((int(company.tax) * int(totalAmount[0][0]))/100)
        discount = math.floor((int(company.discount) * int(totalAmount[0][0])) / 100)

        subtotal = math.floor(int(totalAmount[0][0])+shipping+tax-discount)

        response = make_response(render_template('cart.html', list=table, company=company, totalAmount=totalAmount[0][0], shipping=shipping, tax=tax, discount=discount,subtotal=subtotal,login_email=login_email))
        return response

    qty = request.form["qty"]
    maxQty = request.form["max-qty"]
    bagId = request.form["bag-id"]

    qty = int(qty)
    maxQty = int(maxQty)

    if qty == 0:
        deleteFromCart()

    if qty > maxQty or qty < 0:
        txt = "SELECT @ab:=@ab+1 as SrNo,bag_id,user_id,bag.product_id,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1,product_title,product_size,product_price,product_quantity,bag_quantity,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
        table = db.showTableOne(txt, userId)

        txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
        totalAmount = db.showTableOne(txt, userId)

        txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
        noOfQty = db.showTableOne(txt, userId)
        if noOfQty[0][0] is None:
            response = make_response(
                render_template('cart.html', list=table, company=company, totalAmount=0,
                                shipping=0, tax=0, discount=0, subtotal=0,login_email=login_email))
            return response
        shipping = (int(company.shippingFee) * int(noOfQty[0][0]))

        tax = math.floor((int(company.tax) * int(totalAmount[0][0])) / 100)
        discount = math.floor((int(company.discount) * int(totalAmount[0][0])) / 100)

        subtotal = math.floor(int(totalAmount[0][0]) + shipping + tax - discount)

        if qty > maxQty:
            response = make_response(render_template('cart.html', list=table, company=company, totalAmount=totalAmount[0][0], shipping=shipping,tax=tax, discount=discount, subtotal=subtotal, itemQty=maxQty, errorMsg2="Exceed Quantity",login_email=login_email))
            return response
        else:
            response = make_response(render_template('cart.html', list=table, company=company, totalAmount=totalAmount[0][0],shipping=shipping,tax=tax, discount=discount, subtotal=subtotal,login_email=login_email))
            return response

    txt = "UPDATE firstdatabase.bag SET bag_quantity=%s  where bag_id=%s"
    db.changeQuantity(txt, qty, bagId)
    txt = "SELECT @ab:=@ab+1 as SrNo,bag_id,user_id,bag.product_id,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1,product_title,product_size,product_price,product_quantity,bag_quantity,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    table = db.showTableOne(txt, userId)
    txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
    totalAmount = db.showTableOne(txt, userId)

    txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    noOfQty = db.showTableOne(txt, userId)
    if noOfQty[0][0] is None:
        response = make_response(
            render_template('cart.html', list=table, company=company, totalAmount=0,
                            shipping=0, tax=0, discount=0, subtotal=0,login_email=login_email))
        return response
    shipping = (int(company.shippingFee) * int(noOfQty[0][0]))

    tax = math.floor((int(company.tax) * int(totalAmount[0][0])) / 100)
    discount = math.floor((int(company.discount) * int(totalAmount[0][0])) / 100)

    subtotal = math.floor(int(totalAmount[0][0]) + shipping + tax - discount)

    response = make_response(render_template('cart.html', list=table, company=company, totalAmount=totalAmount[0][0], shipping=shipping,tax=tax, discount=discount, subtotal=subtotal,login_email=login_email))
    return response


@app.route('/deleteFromCart', methods=['GET', 'POST'])
def deleteFromCart():
    company = Company()
    bagId = request.form["bag-id"]
    txt = "delete from bag where bag_id=%s"
    db.removeOne(txt, bagId)

    login_email = request.cookies.get("email")
    userId = db.getInformation(login_email)
    userId = userId[0][0]
    txt = "SELECT @ab:=@ab+1 as SrNo,bag_id,user_id,bag.product_id,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1,product_title,product_size,product_price,product_quantity,bag_quantity,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    table = db.showTableOne(txt, userId)
    txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
    totalAmount = db.showTableOne(txt, userId)

    txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    noOfQty = db.showTableOne(txt, userId)
    if noOfQty[0][0] is None:
        response = make_response(
            render_template('cart.html', list=table, company=company, totalAmount=0,
                            shipping=0, tax=0, discount=0, subtotal=0,login_email=login_email))
        return response
    shipping = (int(company.shippingFee) * int(noOfQty[0][0]))

    tax = math.floor((int(company.tax) * int(totalAmount[0][0])) / 100)
    discount = math.floor((int(company.discount) * int(totalAmount[0][0])) / 100)

    subtotal = math.floor(int(totalAmount[0][0]) + shipping + tax - discount)

    response = make_response(render_template('cart.html', list=table, company=company, totalAmount=totalAmount[0][0], shipping=shipping,tax=tax, discount=discount, subtotal=subtotal,login_email=login_email))
    return response


@app.route('/confirm-order', methods=['GET'])
def confirmOrder():
    company = Company()
    login_email = request.cookies.get("email")

    userId = db.getInformation(login_email)
    userId = userId[0][0]
    txt = "SELECT user_id,bag.product_id,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1,product_title,product_size,product_price,product_quantity,bag_quantity,bag_id FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
    table = db.showTableOne(txt, userId)

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    for x in table:
        if x[6] < x[7]:
            txt = "SELECT @ab:=@ab+1 as SrNo,bag_id,user_id,bag.product_id,product_img,product_title,product_size,product_price,product_quantity,bag_quantity,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
            tables = db.showTableOne(txt, userId)
            txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
            totalAmount = db.showTableOne(txt, userId)
            itemName = x[3]
            itemQty = x[6]

            txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
            noOfQty = db.showTableOne(txt, userId)
            if noOfQty[0][0] is None:
                response = make_response(
                    render_template('cart.html', list=table, company=company, totalAmount=0,
                                    shipping=0, tax=0, discount=0, subtotal=0,login_email=login_email))
                return response

            shipping = (int(company.shippingFee) * int(noOfQty[0][0]))
            tax = math.floor((int(company.tax) * int(totalAmount[0][0])) / 100)
            discount = math.floor((int(company.discount) * int(totalAmount[0][0])) / 100)
            subtotal = math.floor(int(totalAmount[0][0]) + shipping + tax - discount)

            response = make_response(render_template('cart.html', list=tables, company=company, totalAmount=totalAmount[0][0],shipping=shipping,tax=tax, discount=discount, subtotal=subtotal, errorMsg='OUT OF STOCK',itemName=itemName,itemQty=itemQty,login_email=login_email))
            return response

    txt = "SELECT @ab:=@ab+1 as SrNo,bag.product_id,product_title,bag_quantity,product_price,bag_quantity*product_price FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    invoice_table = db.showTableOne(txt, userId)

    txt = "SELECT sum(bag_quantity*product_price) FROM bag,product where user_Id=%s and bag.product_id=product.product_id"
    invoice_totalAmount = db.showTableOne(txt, userId)

    txt = "SELECT sum(bag_quantity) FROM bag,product, (SELECT @ab:= 0) AS ab where user_Id=%s and bag.product_id=product.product_id"
    noOfQty = db.showTableOne(txt, userId)

    invoice_shipping = (int(company.shippingFee) * int(noOfQty[0][0]))
    invoice_tax = math.floor((int(company.tax) * int(invoice_totalAmount[0][0])) / 100)
    invoice_discount = math.floor((int(company.discount) * int(invoice_totalAmount[0][0])) / 100)
    invoice_subtotal = math.floor(int(invoice_totalAmount[0][0]) + invoice_shipping + invoice_tax - invoice_discount)

    for x in table:
        changeQty = x[6]-x[7]
        productId = x[1]
        bagId = x[8]
        orderQty = x[7]
        txt = "UPDATE firstdatabase.product SET product_quantity=%s  where product_id=%s"
        db.changeQuantity(txt, changeQty, productId)
        txt = "insert into firstdatabase.order (order_quantity,product_id) values (%s,%s)"
        db.changeQuantity(txt, orderQty, productId)
        txt = "SELECT * FROM firstdatabase.order ORDER BY order_id DESC LIMIT 0, 1;"
        orderId = db.report(txt)
        txt = "insert into firstdatabase.orderdetail (orderdetail_datetime,order_id,user_id,orderdetail_status) values (%s,%s,%s,'pending')"
        db.three(txt, dt_string, orderId[0][0], userId)
        txt = "delete from firstdatabase.bag where bag_id=%s"
        db.removeOne(txt, bagId)

    invoice_totalAmount = str(invoice_totalAmount[0][0])
    invoice_shipping = str(invoice_shipping)
    invoice_tax = str(invoice_tax)
    invoice_discount = str(invoice_discount)
    invoice_subtotal = str(invoice_subtotal)


    msg = Message('Order Receipt', sender=senderEmail, recipients=[login_email])
    msg.body = "We have attached your receipt to this email."

    fr = open("invoice-header.html", "r")
    fw = open("invoice.html", "w")
    fw.write(fr.read())
    fr.close()
    fw.close()

    fw = open("invoice.html", "a")

    for x in invoice_table:
        str0 = str(x[0])
        str1 = str(x[1])
        str2 = str(x[2])
        str3 = str(x[3])
        str4 = str(x[4])
        str5 = str(x[5])
        fw.write("<tr><td>" + str0 + "</td><td>" + str1 + "</td><td>" + str2 + "</td><td>" + str3 + "</td><td>" + str4 + "</td><td>" + str5 + "</td></tr>")

    fw.write('</tbody></table></div><h4 style="padding-left: 75%;color: #04AA6D">TOTAL PKR ' + invoice_totalAmount + '</h4><h4 style="padding-left: 75%;color: #04AA6D">SHIPPING PKR ' + invoice_shipping + '</h4><h4 style="padding-left: 75%;color: #04AA6D">TAX PKR ' + invoice_tax + '</h4><h4 style="padding-left: 75%;color: #04AA6D">DISCOUNT PKR ' + invoice_discount + '</h4><h4 style="padding-left: 75%;color: #04AA6D">SUBTOTAL PKR ' + invoice_subtotal + '</h4>')

    fr = open("invoice-footer.html", "r")
    fw.write(fr.read())

    fr.close()
    fw.close()

    conf = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdfkit.from_file('invoice.html', 'invoice.pdf', configuration=conf)

    with app.open_resource("invoice.pdf") as fp:
        msg.attach("invoice.pdf", "invoice/pdf", fp.read())

    mail.send(msg)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2  FROM firstdatabase.product where product_category LIKE 'MEN%' and product_status='active' order by product_id desc Limit 0,6"
    menLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'MEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    menBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'WOMEN%' and product_status='active' order by product_id desc Limit 0,6"
    womenLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'WOMEN%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    womenBestSale = db.showTableZero(txt)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM firstdatabase.product where product_category LIKE 'KIDS%' and product_status='active' order by product_id desc Limit 0,6"
    kidsLatest = db.showTableZero(txt)

    txt = "SELECT order.product_id,product_title,concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price,product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2, SUM(order_quantity) as TotalQuantity FROM firstdatabase.order,firstdatabase.product,firstdatabase.orderdetail where order.product_id=product.product_id and order.order_id=orderdetail.order_id and product_category LIKE 'KIDS%' and product_status='active' GROUP BY order.product_id order by TotalQuantity desc Limit 0,6"
    kidsBestSale = db.showTableZero(txt)

    response = make_response(
        render_template('index.html', company=company, menLatest=menLatest, menBestSale=menBestSale,
                        womenLatest=womenLatest, womenBestSale=womenBestSale, kidsLatest=kidsLatest,
                        kidsBestSale=kidsBestSale, login_email=login_email, order_msg="ok"))

    return response


@app.route('/view-product-detail', methods=['POST'])
def product_detail():
    company = Company()
    product_id = request.form["product-id"]
    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM product where product_id=%s"
    product = db.showTableOne(txt, product_id)

    login_email = request.cookies.get("email")

    if login_email is None or login_email == "":
        response = make_response(render_template('product-detail.html', company=company, product=product, not_login="not"))
    else:
        response = make_response(render_template('product-detail.html', company=company, product=product, login_email=login_email))

    return response


@app.route('/view-product-detail-place-order', methods=['POST'])
def view_product_detail_place_order():
    company = Company()
    product_id = request.form["product-id"]

    login_email = request.cookies.get("email")
    productId = request.form["product-id"]
    userId = db.getInformation(login_email)
    userId = userId[0][0]

    if db.productExistInBag(userId, productId) == True:
        db.increamentProductInBag(userId, productId)
    else:
        db.addProductInBag(userId, productId)

    txt = "SELECT product_id, product_title, concat('static/product_photo/',SUBSTRING_INDEX(product_img, ':', 1)) AS product_img_1, product_price, product_quantity, product_category, product_size,product_desc,concat('static/product_photo/',SUBSTRING_INDEX(SUBSTRING_INDEX(product_img,' ', 2), ':',-1)) as product_img_2 FROM product where product_id=%s"
    product = db.showTableOne(txt, product_id)

    msg = "Item Added to Cart Successfully!"
    response = make_response(render_template('product-detail.html', company=company, product=product, login_email=login_email, msg=msg))
    return response


if __name__ == '__main__':
    app.run(debug=True)