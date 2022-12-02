import random

def generateOTP():
    return random.randrange(100000,999999)


import os
from twilio.rest import Client

def signup_message():
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    otp= generateOTP()
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create(  
                                body = f"Your OTP is {otp}",
                                from_ = '+18064911715',   
                                to = '+2348058897120'
                            ) 
    
    print(message.sid)

def verify_sms_otp():
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    verify_sid = 'VA5ece9a2f60d31e844fb899b2389d9233'
    client = Client(account_sid, auth_token)

    verification = client.verify.services('verifySid').verifications.create(to='+2348058897120', channel='sms')

    print(verification.status)

    otp_code = input("Please enter the OTP:")

    verification_check = client.verify.services('verifySid').verification_checks.create(to='+2348058897120', code=otp_code)

    print(verification_check.status)




# def signup_message(signupmail):
#     account_sid = os.environ['TWILIO_ACCOUNT_SID']
#     auth_token = os.environ['TWILIO_AUTH_TOKEN']
#     otp= generateOTP()
#     client = Client(account_sid, auth_token) 
    
#     message = client.messages.create(  
#                                 body = f"Your OTP is {otp}",
#                                 from_ = '+18064911715',   
#                                 to = signupmail
#                             ) 
    
#     print(message.sid)
# # +13465508501
# +18064911715