from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import select
from datetime import datetime
#date = db.Column(db.dateTime(timezone=True), default=func.now())
#user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # doesn't need caps
#notes = db.relationship('Note') # caps here

"""
This file is what makes up the database. 
Each class is a table in the database.
This is a python way of mixing databases and objs. 
when we want to access a value in the database we have to query the database and we get object returned of the values. but you are also able to use functions such as seen in the user class
some querys look like this CLASSNAME.query.filter_by(value=value).first() this will get the first value with the value == to the value. you can also do ordering. 
if you want to get all the values do .query.all(). this will return you a list of all the row objects. 
"""

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    secondname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(512))
    role_id = db.Column(db.Integer, db.ForeignKey('userrole.id'))
    orders = db.relationship('Order')
    basket = db.relationship('Userbasket')
    authcodes = db.relationship('Authcode')
    files = db.relationship('Userfiles')

    def get_files(self):
        files = Userfiles.query.filter_by(user_id=self.id).all()
        return files
    
    def get_orders(self):
        my_orders = Order.query.filter_by(user_id=self.id).all()
        return my_orders

class Userfiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file = db.Column(db.String(200))
    

class Userrole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(200))
    users = db.relationship('User')

class Userbasket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(50))
    series = db.Column(db.String(50))
    description = db.Column(db.String(200))
    image = db.Column(db.String(200))
    price = db.Column(db.Float())
    order = db.relationship('Order')
    stock = db.relationship('Stock')
    basket = db.relationship('Userbasket')

    def get_stock_level(self):
        stock = Stock.query.filter_by(car_id=self.id).first()
        return stock.level
    
    def get_stock_numberOfCarsSold(self):
        stock = Stock.query.filter_by(car_id=self.id).first()
        return stock.numberOfCarsSold

class Deliveryaddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    houseNumber = db.Column(db.String(5))
    roadName = db.Column(db.String(150))
    town = db.Column(db.String(150))
    county = db.Column(db.String(150))
    postcode = db.Column(db.String(10))
    orders = db.relationship('Order')

class Orderstatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(150))
    orders = db.relationship('Order')

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    level = db.Column(db.Integer)
    numberOfCarsSold = db.Column(db.Integer)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    last4carddigits = db.Column(db.String(4))
    amount = db.Column(db.Float())
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('deliveryaddress.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('orderstatus.id'))
    carprice = db.Column(db.Float())
    pricePaid = db.Column(db.Float())
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    payments = db.relationship('Payment')

    def get_address_postcode(self):
        address = Deliveryaddress.query.filter_by(id=self.address_id).first()
        return address.postcode
    
    def get_address_housenumber(self):
        address = Deliveryaddress.query.filter_by(id=self.address_id).first()
        return address.houseNumber
    
    def get_address_roadname(self):
        address = Deliveryaddress.query.filter_by(id=self.address_id).first()
        return address.roadName
    
    def get_address_town(self):
        address = Deliveryaddress.query.filter_by(id=self.address_id).first()
        return address.town
    
    def get_address_county(self):
        address = Deliveryaddress.query.filter_by(id=self.address_id).first()
        return address.county
    
    def get_display_date(self):
        date_time = datetime.fromtimestamp(self.timestamp)
        return date_time.strftime("%d %B, %Y")
    
    def get_display_status_name(self):
        status = Orderstatus.query.filter_by(id=self.status_id).first()
        return status.name
    
    def get_display_status_description(self):
        status = Orderstatus.query.filter_by(id=self.status_id).first()
        return status.description
    
    def get_car_image(self):
        car = Car.query.filter_by(id=self.car_id).first()
        return car.image
    
    def get_car_description(self):
        car = Car.query.filter_by(id=self.car_id).first()
        return car.description
    
class Authcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(6))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
        



      
      

      
      

