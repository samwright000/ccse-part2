from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Authcode
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import validation
import smtplib
from email.mime.text import MIMEText

from email.message import EmailMessage
import ssl
import smtplib

import secrets
import string

from datetime import datetime

auth = Blueprint('auth', __name__)

"""
all the functions below follow the same framework. 
@auth.route means in files route. This are the urls which are to be used to access this function. at the end of the function it always displays
a pay by returning a render template which is part of the flask library. 
They can GET and POST request. When something is posted this means it is reviving data from the website.
All functions automatically GET as they return a html file. 

all the pages work by firstly rendering the template. this is because when loading the page nothing will ever be posted so none of the if conditions will be meet.
this means first time the page is load it will display the page. 
"""

"""
The function below logs a user in. It starts of by checking if the function has been called due to POST, this would occur when a form has been filled in.
It also checks to see if it is from the login-user form. 
If it is then it gets the email and password from the form and checks this with the database.
If something come back from the email then it checks the users password against the entered one. 
If also checks to see if the role id is 1, if it does that means its an admin and 2fa is required.
if not then it just logs the user in if it is valid and if it is not then displays an error. 

the 2fa works by generating a random 6 digits code form letters and numbers. this is then entered into the auth database with the users id and code and timestamp. 
"""
@auth.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST' and "login-user" in request.form:
        print("login started")
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                if user.role_id == 1:
                    N = 6
                    # using secrets.choice()
                    # generating random strings

                    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(N))
                    
                    code = str(res)
                    
                    # This is where the code is entered into the database
                    new_auth = Authcode(user_id=user.id, code=generate_password_hash(code,method='sha256'))
                    db.session.add(new_auth)
                    db.session.commit()
                    
                    #This code below creates an email and enters the code into it, this is what is sent to the admin's emails 
                    smtp_server = "smtp.gmail.com"
                    sender_email = "ccsepart1@gmail.com"
                    receiver_email = email
                    password = "whhaihwkzkeuzqaw"#12345WarwickUNI2023
                    port = 465
                    body = """
                    Hello, 

                    Here is your 2 factor authenticaion email code: {}

                    Please return back into the website and enter this code.

                    Wright n Motors 
                    """.format(code)

                    subject = "This is the subject"

                    em = EmailMessage()
                    em['From'] = sender_email
                    em['To'] = receiver_email
                    em['Subject'] = subject
                    em.set_content(body)

                    context = ssl.create_default_context()

                    # the email is sent here. 
                    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, em.as_string())
                                        
                    #it then redirects the user to the auth page. 
                    return redirect(url_for('auth.auth_user',user_id=user.id))
                
                # this is where the user gets logged in, it passes in the user object from the database and automatically makes the user be remebered 
                login_user(user, remember=True)
                flash('Logged In Successfully!', category='success')# Flash means a message is displayed on the webpage. 
                
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect User Details, Try Again...',category='error')
        else:
            flash('Incorrect User Details, Try Again...',category='error')

            
    return render_template('login.html', user=current_user)

"""


This function is ran if the user is an admin. it checks to see if a form is posted. 
the code the user has entered is check with the most recented one in the database. 
the time the code is in the database and the time the user has entered it is also check, if it is over 5 mins the code will not work. 
"""
@auth.route('/auth_user/<user_id>', methods=['GET','POST'])
def auth_user(user_id):
    if request.method == 'POST' and "auth-user" in request.form:

        user_entered_code = request.form.get('auth-user')
        gen_code = Authcode.query.filter_by(user_id=user_id).order_by(Authcode.timestamp.desc()).first()

        #the code below just converts the time stamped stored into an int so maths can be done to it. 
        gen_code_timestamp = str(gen_code.timestamp)

        date_time = datetime.strptime(gen_code_timestamp, '%Y-%m-%d %H:%M:%S')

        ts = date_time.timestamp()

        current_dt = datetime.now()

        current_ts = datetime.timestamp(current_dt)

        #this is checking if it is over 5 mins from the code being created to being entered 
        difference = current_ts - ts

        if difference > 300:
            flash('Logged Not Successfully!', category='error')
            return redirect(url_for('views.home'))


        #the coded is hashed is checks to see if the code entered could back the code stored. 
        # as the password has already been check we only check the password. 
        if check_password_hash(gen_code.code, user_entered_code):
            user = User.query.filter_by(id=user_id).first()
            flash('Logged In Successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
            

    return render_template("auth-user.html")

"""
This code just logs the user out.
"""
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



"""
The code below is to create a user. it starts by getting all the data from the user, checking it then entering it into the database if it is valid.
It then automatically logs the user in
"""
@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():

    if request.method == "POST":
        firstname = request.form.get('firstname')
        secondname = request.form.get('secondname')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        user = User.query.filter_by(email=email).first()

        """
        The code below is all about checking to make sure the input is valid. 
        first checks if the user excits already then checks to make sure the data to create the new video is valid 
        """
        if user:
            flash('User Already Exists.',category='error')

        elif len(firstname) < 1:
            flash("First name not filled in",category='error')
        elif len(secondname) < 1:
            flash("Second name not filled in",category='error')
        elif password != password_confirm:
            print(password +" "+ password_confirm)
            flash("Passwords do not match",category='error')
        elif len(password) < 7:
            flash("Passwords must be greater than 7 char",category='error')
        else:
            new_user = User(firstname=firstname, secondname=secondname, email=email,password=generate_password_hash(password,method='sha256'),role_id=5)# this creates the object to be entered 
            db.session.add(new_user)
            db.session.commit()# this is where the user is entered into the database
            flash("Account Create!",category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template('sign-up.html', user=current_user)

