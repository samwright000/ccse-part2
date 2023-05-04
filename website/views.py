from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Car, Userbasket, Order, Deliveryaddress, Stock, Userfiles, Orderstatus
from . import db
from . import validation as valid

from sqlalchemy import select

import os
from werkzeug.utils import secure_filename
import time

from werkzeug.security import generate_password_hash, check_password_hash

views = Blueprint('views', __name__)

"""
In this file is stores all the other views.
This is all the pages you want to access on the database. 
"""


"""
This route is the default page you access when putting in the ip of the website. 
This functions is the view cars page. This displays all the cars you can buy.

It starts by getting all the cars in the car table. 

the post is check to see if a car is added to the basket. 
It also doubles check to see if the user has been logged in. 
the form automically posteds the id of the car. this is then entered into the database which enters the user id and car id. 

this then displays a confirmation message that the car has been added.
"""

@views.route("/", methods=['GET','POST'])
def home():

    cars = Car.query.all()
     
    if request.method == "POST":
        if current_user.id:
            car_id = request.form.get('code')

            basket_entry = Userbasket(car_id=car_id, user_id=current_user.id)
            db.session.add(basket_entry)
            db.session.commit()

            car_add = Car.query.filter_by(id=car_id).first()

            message = "{}{} has been added to your basket!".format(car_add.model,car_add.series)

            flash(message, category='success')
            
            return redirect(url_for("views.home"))    
    return render_template("home.html", user=current_user, cars=cars)


"""
This is the basket page. if no forms are posted then it gets all the car id for the rows which has the user id in. 
this is then passed to the html code as a list. 
If a form has been posted with id remove-car it will remove the car from the table and then update website. 
"""
@views.route("/basket", methods=['GET','POST'])
@login_required
def basket():
    try:
        if request.method == 'POST' and request.form['remove-car']:
            
            car_id = request.form.get('remove-car')

            car_remove = Userbasket.query.filter_by(car_id=car_id).first()
            db.session.delete(car_remove)
            db.session.commit()
    except:
        pass


    car_ids = []

    car_objects = []

    users_basket = Userbasket.query.filter_by(user_id=current_user.id).all()

    for entry in users_basket:
        car_ids.append(entry.car_id)

    for car in car_ids:
        car_to_add = Car.query.filter_by(id=car).first()

        car_objects.append(car_to_add)

    return render_template("basket.html",user=current_user, cars = car_objects, numberOfCars=len(car_objects))



"""
This code displays all the users cars they have bought. 
"""
@views.route("/mycars", methods=['GET','POST'])
@login_required
def mycars():

    """
    This if checks to see if the form posted was to get a file.
    The file_name is automally entered passed in the form. 
    this then ask if the user wants to download it then, it is done so. 
    """
    if request.method == "POST" and "file_name" in request.form:
        file_name = request.form.get('file_name')
        directory = "C:\\Users\\Samual Wright\\Desktop\\Coding\\Uni\\cardealershippython\\website\\userfiles"+"\\"+file_name
        print(directory)
        return send_file(directory,as_attachment=True)
    

    """
    This function below is to remove a file from system
    it gets the name of the file to be removed. it then querys the database for the users id and the file name
    this is because many users could enter the same named file. 
    this is then removed from the user file database which stores all the files to the users name but then also removes the actual file from the database. 
    
    """
    
    if request.method == "POST" and "remove_file" in request.form:
        file_name = request.form.get('remove_file')
        print("REMOVE: "+str(file_name))

        to_delete = Userfiles.query.filter_by(user_id=current_user.id, file=file_name).first()
        db.session.delete(to_delete)
        db.session.commit()

        os.remove("C:\\Users\\Samual Wright\\Desktop\\Coding\\Uni\\cardealershippython\\website\\userfiles"+"\\"+file_name)

    """
    This function displays the menu for making payment
    """
    if request.method == "POST" and "make-payment" in request.form:
        order_id = request.form.get('make-payment')
        
        order = Order.query.filter_by(id=order_id).first()
        
       
        return render_template("payment.html",user=current_user,my_order=order)
    
    """
    When the user enters a form in the make payment page this if is then ran.
    this gets all the information entered checks them then enters the payment into the payment table

    it then updates the amount paid in the order table and it also checks to see if it is paid off or not
    if it is paid off then the status is also updated.
    """
    if request.method == "POST" and "making-payment" in request.form:

        amount = request.form.get('amount') 
        order_id = request.form.get('making-payment') 

        bankcard = request.form.get('bank-card') 
        cvv = request.form.get("cvv")
        expire_month = request.form.get("expire-month")
        expire_year = request.form.get("expire-year")

        order = Order.query.filter_by(id=order_id).first()

        amount_left = order.carprice - order.pricePaid
        
        if len(bankcard) !=16 or bankcard.isdigit() == False:
            flash('Please Enter Valid Bank Card Number',category='error') 
            return render_template("payment.html",user=current_user,my_order=order)
        
        elif len(cvv) != 3 or cvv.isdigit() == False:
            flash('Please Enter Valid CVV',category='error') 
            return render_template("payment.html",user=current_user,my_order=order)

        elif len(expire_month) < 1 or len(expire_month) > 2 or expire_month.isdigit() == False:
            flash('Please Enter Valid Expire Month',category='error')
            return render_template("payment.html",user=current_user,my_order=order)

        elif len(expire_year) !=2 and len(expire_year) !=4 or expire_year.isdigit() == False:
            flash('Please Enter Valid Expire Year',category='error')
            return render_template("payment.html",user=current_user,my_order=order)

        elif amount.isdigit() == False or float(amount) > float(amount_left):
            flash('Invalid amount',category='error')
            return render_template("payment.html",user=current_user,my_order=order)
        
        else:
            
            order.pricePaid = order.pricePaid+float(amount)
            db.session.commit()

            if order.pricePaid == order.carprice:
                order.status_id = 2
                db.session.commit()



    my_cars = []

    my_orders = Order.query.filter_by(user_id=current_user.id).all()

    for my_order in my_orders:
        my_cars.append(Car.query.filter_by(id=my_order.car_id).first())

    return render_template("mycars.html", user=current_user, my_orders=my_orders, my_cars=my_cars)


"""
******

The rest of the code basically works the same way. It displays data, then waits for a user input then updates a database. 
It all basically works the same way as above. 

******
"""





@views.route("/checkout/<car_id>", methods=['GET','POST'])
@login_required
def checkout(car_id):
    
    car_to_add = Car.query.filter_by(id=car_id).first()
    

    return render_template("checkout.html",user=current_user, car=car_to_add)

@views.route("/oneoffpayment/<car_id>", methods=['GET','POST'])
@login_required
def oneoffpayment(car_id):

    if request.method == "POST":
        
        bankcard = request.form.get('bank-card') 
        cvv = request.form.get("cvv")
        expire_month = request.form.get("expire-month")
        expire_year = request.form.get("expire-year")
        housenumber = request.form.get("housenumber")
        roadname = request.form.get("roadname")
        city = request.form.get("city")
        county = request.form.get("county")
        postcode = request.form.get("postcode")

        if len(bankcard) !=16 or bankcard.isdigit() == False:
            flash('Please Enter Valid Bank Card Number',category='error') 
        
        elif len(cvv) != 3 or cvv.isdigit() == False:
            flash('Please Enter Valid CVV',category='error') 

        elif len(expire_month) < 1 or len(expire_month) > 2 or expire_month.isdigit() == False:
            flash('Please Enter Valid Expire Month',category='error')

        elif len(expire_year) !=2 and len(expire_year) !=4 or expire_year.isdigit() == False:
            flash('Please Enter Valid Expire Year',category='error')

        elif valid.checkforsqlinjection(city) == 1 and len(city) < 150:
            flash('Please Enter Valid Town/City',category='error')

        elif valid.checkforsqlinjection(roadname) == 1 and len(roadname) < 150:
            flash('Please Enter Valid Road Name',category='error')

        elif valid.checkforsqlinjection(county) == 1 and len(county) < 150:
            flash('Please Enter Valid County',category='error')

        elif valid.checkforsqlinjection(postcode) == 1 and len(postcode) < 10:
            flash('Please Enter Valid postcode (10 digits or less)',category='error')

        else:

            car_to_add = Car.query.filter_by(id=car_id).first()

            new_address = Deliveryaddress(houseNumber=housenumber, roadName=roadname, town=city, county=county, postcode=postcode)
            db.session.add(new_address)
            db.session.commit()

            new_order = Order(user_id=current_user.id, car_id=car_to_add.id, address_id=new_address.id,status_id=2,carprice=car_to_add.price, pricePaid=car_to_add.price)

            db.session.add(new_order)
            db.session.commit()

            stock = Stock.query.filter_by(car_id=car_id).first()
            stock.level = stock.level - 1
            stock.numberOfCarsSold = stock.numberOfCarsSold + 1
            db.session.commit()
            
            try:
                to_delete = Userbasket.query.filter_by(user_id=current_user.id, car_id=car_to_add.id).first()
                db.session.delete(to_delete)
                db.session.commit()
                
            except:
                pass

            return render_template("closestdealer.html",user=current_user)   



    car_ids = []

    total_balance = 0

    users_basket = Userbasket.query.filter_by(user_id=current_user.id).all()

    for entry in users_basket:
        car_ids.append(entry.car_id)

    for car in car_ids:
        car_to_add = Car.query.filter_by(id=car).first()

        total_balance = car_to_add.price
    
    return render_template("oneoffpayment.html",user=current_user, total_balance=total_balance)






@views.route("/paybyfinance/<car_id>", methods=['GET','POST'])
@login_required
def paybyfinance(car_id):

    if request.method == "POST":
        
        bankcard = request.form.get('bank-card') 
        cvv = request.form.get("cvv")
        expire_month = request.form.get("expire-month")
        expire_year = request.form.get("expire-year")
        housenumber = request.form.get("housenumber")
        roadname = request.form.get("roadname")
        city = request.form.get("city")
        county = request.form.get("county")
        postcode = request.form.get("postcode")

        if len(bankcard) !=16 or bankcard.isdigit() == False:
            flash('Please Enter Valid Bank Card Number',category='error') 
        
        elif len(cvv) != 3 or cvv.isdigit() == False:
            flash('Please Enter Valid CVV',category='error') 

        elif len(expire_month) < 1 or len(expire_month) > 2 or expire_month.isdigit() == False:
            flash('Please Enter Valid Expire Month',category='error')

        elif len(expire_year) !=2 and len(expire_year) !=4 or expire_year.isdigit() == False:
            flash('Please Enter Valid Expire Year',category='error')

        elif valid.checkforsqlinjection(city) == 1 and len(city) < 150:
            flash('Please Enter Valid Town/City',category='error')

        elif valid.checkforsqlinjection(roadname) == 1 and len(roadname) < 150:
            flash('Please Enter Valid Road Name',category='error')

        elif valid.checkforsqlinjection(county) == 1 and len(county) < 150:
            flash('Please Enter Valid County',category='error')

        elif valid.checkforsqlinjection(postcode) == 1 and len(postcode) < 10:
            flash('Please Enter Valid postcode (10 digits or less)',category='error')

        else:

            car_to_add = Car.query.filter_by(id=car_id).first()

            new_address = Deliveryaddress(houseNumber=housenumber, roadName=roadname, town=city, county=county, postcode=postcode)
            db.session.add(new_address)
            db.session.commit()

            new_order = Order(user_id=current_user.id, car_id=car_to_add.id, address_id=new_address.id,status_id=1,carprice=car_to_add.price, pricePaid=0)

            db.session.add(new_order)
            db.session.commit()

            stock = Stock.query.filter_by(car_id=car_id).first()
            stock.level = stock.level - 1
            stock.numberOfCarsSold = stock.numberOfCarsSold + 1
            db.session.commit()
            
            try:
                to_delete = Userbasket.query.filter_by(user_id=current_user.id, car_id=car_to_add.id).first()
                db.session.delete(to_delete)
                db.session.commit()
                
            except:
                pass

            return redirect(url_for("views.uploadfiles"))    



    car_ids = []

    total_balance = 0

    users_basket = Userbasket.query.filter_by(user_id=current_user.id).all()

    for entry in users_basket:
        car_ids.append(entry.car_id)

    for car in car_ids:
        car_to_add = Car.query.filter_by(id=car).first()

        total_balance = car_to_add.price
    
    return render_template("paybyfinance.html",user=current_user, total_balance=total_balance)


@views.route("/uploadfiles", methods=['GET','POST'])
@login_required
def uploadfiles():

    allowed_extentions = {"pdf","png","jpg","jpeg"}

    if request.method == "POST":
        if request.files:
            file = request.files["image"]
            size = request.cookies.get("filesize")
            #this checks to see how large the file is 
            if int(size) > 5000000:
                flash("File Not Uploaded",category='error')
            
            elif '.' in file.filename and file.filename.rsplit(".",1)[1].lower() in allowed_extentions:
                filename = secure_filename(file.filename)
                filename = "userid-{}-time-{}-filename-{}".format(str(current_user.id),int(round(time.time())),str(filename))
                file.save(os.path.join(r"C:\Users\Samual Wright\Desktop\Coding\Uni\cardealershippython\website\userfiles", filename))
                
                new_file = Userfiles(user_id=current_user.id, file=filename)
                db.session.add(new_file)
                db.session.commit()
                flash("File Uploaded",category='success')

            else:
                flash("File Not Uploaded",category='error')

    return render_template("uploadfiles.html",user=current_user)

#https://www.youtube.com/watch?v=6WruncSoCdI&t=223s




@views.route("/admin")
@login_required
def admin():
    if current_user.role_id != 1:
        return redirect("/")
    
    return render_template("admindash.html",user=current_user)

@views.route("/carmanager", methods=['GET','POST'])
@login_required
def carmanager():
    if current_user.role_id != 1:
        return render_template("home.html",user=current_user)
    
    if request.method == 'POST' and "create-car" in request.form:
        model = request.form.get('model')
        series = request.form.get('series')
        description = request.form.get('description')
        image = request.form.get('image')
        price = request.form.get('price')
        stock = request.form.get('stock')


        new_car= Car(model=model, series=series, description=description, image=image, price=price)
        db.session.add(new_car)
        db.session.commit()

        new_stock = Stock(car_id=new_car.id, level=int(stock),numberOfCarsSold=0)
        db.session.add(new_stock)
        db.session.commit()

    if request.method == 'POST' and "edit-car" in request.form:
        model = request.form.get('model')
        series = request.form.get('series')
        description = request.form.get('description')
        image = request.form.get('image')
        price = request.form.get('price')
        stock = request.form.get('stock')
        car_id = request.form.get('id')
        amount_sold = request.form.get('amountsold')
        editing_car = Car.query.filter_by(id=car_id).first()

        try:

            if model:
                editing_car.model = model

            if series:
                editing_car.series = series

            if description:
                editing_car.description = description

            if image:
                editing_car.image = image

            if price:
                editing_car.price = price

            if stock:
                editing_stock = Stock.query.filter_by(car_id=car_id).first()
                editing_stock.level = stock

            if amount_sold:
                editing_stock = Stock.query.filter_by(car_id=car_id).first()
                editing_stock.numberOfCarsSold = amount_sold
        except:
            pass
            
        db.session.commit()

    if request.method == 'POST' and "remove-car" in request.form:
        try:
            car_id = request.form.get('id')
            to_delete = Car.query.filter_by(id=car_id).first()
            db.session.delete(to_delete)
            db.session.commit()
        except:
            pass
    
    cars = Car.query.all()
    return render_template("carmanager.html",user=current_user, cars=cars)

@views.route("/usermanager", methods=['GET','POST'])
@login_required
def usermanager():
    if current_user.role_id != 1:
        return render_template("home.html",user=current_user)
    

    if request.method == 'POST' and "edit-user" in request.form:
        firstname = request.form.get('firstname')
        secondname = request.form.get('secondname')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role_id')
        id = request.form.get('id')

        editing_user = User.query.filter_by(id=id).first()

        try:

            if firstname:
                editing_user.firstname = firstname

            if secondname:
                editing_user.secondname = secondname

            if email:
                editing_user.email = email

            if password:
                editing_user.password = generate_password_hash(password,method='sha256')

            if role:
                editing_user.role = role

            db.session.commit()
        except:
            pass

    
    if request.method == 'POST' and "remove-user" in request.form:
        try:
            user_id = request.form.get('id')
            to_delete = User.query.filter_by(id=user_id).first()
            db.session.delete(to_delete)
            db.session.commit()
        except:
            pass

    
    if request.method == "POST" and "file_name" in request.form:
        file_name = request.form.get('file_name')
        directory = "C:\\Users\\Samual Wright\\Desktop\\Coding\\Uni\\cardealershippython\\website\\userfiles"+"\\"+file_name
        print(directory)
        return send_file(directory,as_attachment=True)
    
    customers = User.query.all()

    
    
    
    return render_template("usermanager.html",user=current_user,customers=customers)

@views.route("/financemanager", methods=['GET','POST'])
@login_required
def financemanager():
    if current_user.role_id != 1:
        return render_template("home.html",user=current_user)
    
    if request.method == 'POST' and "edit-order-status" in request.form:
        new_status_id = request.form.get('new-status-id')
        order_id = request.form.get('order-id')

        editing_order = Order.query.filter_by(id=order_id).first()

        try:

            if new_status_id:
                editing_order.status_id = new_status_id

            db.session.commit()
        except:
            pass
    



    statuss = Orderstatus.query.all()
    
    return render_template("financemanager.html",user=current_user, statuss=statuss)

@views.route("/cardealerlocation", methods=['GET','POST'])
@login_required
def cardealerlocation():

    return render_template("closestdealer.html",user=current_user)

    
