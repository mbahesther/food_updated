import os
import ssl
import smtplib
from datetime import datetime, date, timedelta, time
import datetime
from flask import url_for
from email.message import EmailMessage
from run import  mydb, MySQLdb, my_cursor

import random

#generate otp
def generateOTP():
    return random.randrange(100000,999999)

#expire time for the otp
def email_expire_time():
    now = datetime.datetime.now()
    expire= now + timedelta(minutes=10)
    dt_now = expire.strftime("%d-%m-%Y %H:%M:%S")
    expire_time = dt_now
    return (expire_time)


#email to verify otp after registering
def signup_mail(signupmail):
        email_sender = 'omanovservices@gmail.com'
        email_password = os.getenv('EMAIL_PASSWORD')
        email_receiver = signupmail
        subject = "Registration Confirmation"
        otp = generateOTP()
        expire_time= email_expire_time()
      
        body = (f''' Thank you for registering on Foods. Please confirm your email by clicking on link below and use single-use \033 {otp}  \033 as code. \n link: {url_for('verify_email_otp', _external=True)}  \n If you can't click copy and paste in the broswer  ''' )
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('UPDATE signup SET email_otp=%s, expire_email_otp=%s WHERE email = %s', [otp, expire_time ,signupmail])
        mydb.commit()
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())


#route the otp if the user didnt get the first time
def resend_email(useremail):
        email_sender = 'omanovservices@gmail.com'
        email_password = os.getenv('EMAIL_PASSWORD')
        email_receiver = useremail
        subject = "Please confirm your email"
        otp = generateOTP()
      
        body = (f'''Please confirm your email by clicking on link below and use single-use \033 {otp}  \033 as code. \n link: {url_for('verify_email_otp', _external=True)}  \n If you can't click copy and paste in the broswer  ''' )
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('UPDATE signup SET email_otp=%s WHERE email = %s', [otp, useremail])
        mydb.commit()
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    


# body =  url_for('register', otp=generateOTP, _external=True)             


