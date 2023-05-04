from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
print("2")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "45!2-stop_CtPaswTwwwQ12ZX3_12-234kghq!" # This secures the communication 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    #app.config["IMAGE_UPLOADS"] = "C:\Users\Samual Wright\Desktop\Coding\Uni\cardealershippython\website\userfiles"
    db.init_app(app)

    

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/') # this means the prefix before each route is nothing. you could change this so that certain views have an automatic prefex. 
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Userrole, Car, Deliveryaddress, Orderstatus, Stock, Payment, Order, Userbasket

    with app.app_context():
        db.create_all()

    """
    The code below is to log the user in so that we are able to refence the users information from the database globablly around the code. 
    """

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


"""
This creates a database if there isn't already one. 
"""
def create_database(app):
    print("startin")
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")