"""
This code is just used to test using the 2fa
"""

from email.message import EmailMessage
import ssl
import smtplib

import secrets
import string
 
# initializing size of string
N = 6
 
# using secrets.choice()
# generating random strings
res = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(N))

smtp_server = "smtp.gmail.com"
sender_email = "ccsepart1@gmail.com"
receiver_email = "samualwright@outlook.com"
password = "whhaihwkzkeuzqaw"#12345WarwickUNI2023
port = 465
body = """
Hello, thank you for creating an account with Wright n Motors. 

Here is your 2 factor authenticaion email code: {}

Please return back into the website and enter this code. 
""".format(res)

subject = "This is the subject"

em = EmailMessage()
em['From'] = sender_email
em['To'] = receiver_email
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()


with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, em.as_string())