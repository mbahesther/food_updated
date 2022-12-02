from run import *
from passlib.hash import pbkdf2_sha256 as sha256

from extension.signupmail import signup_mail, resend_email
from extension.forgetmail import forget_password
from datetime import datetime, date, timedelta, time
import datetime

import jwt as JWTT

#signup user
@app.route('/api/user/signup', methods= ['POST'])
def signup():
    data = request.json
    fullname = data['fullname']
    email = data['email']
    phone_number = data['phone_number']
    password = data['password']
    
    if len(phone_number) !=14:
            return jsonify({'msg':'Your phone number is invalid'}),400
    else:      
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('''SELECT * FROM signup WHERE email =%s ''', [email])
        user = my_cursor.fetchone()
        if user:
            return jsonify({'msg':'Email already exits, use another email'}),400
        else:
         
            my_cursor.execute('''SELECT * FROM signup WHERE phone_number =%s''', [phone_number])
            query = my_cursor.fetchone()
            if query is None:
                hash_password = sha256.hash(password)  
                       
                #send_phone = signup_message()
                my_cursor.execute('INSERT INTO signup(fullname, email, phone_number, password) VALUES(%s, %s, %s, %s)', [fullname, email, phone_number, hash_password])
                send_email = signup_mail(email) 
                mydb.commit()      
                   
                return jsonify({'success': True,'msg':'Registration successful, An otp is sent to your email and phone number verify it'}),200
                  
            else:           
                 return jsonify({'msg':'This phone number is already registered'}),400
            
#verify otp
@app.route('/api/user/verify_email_otp', methods=['POST'])
def verify_email_otp():
    data = request.json
    otp = data['otp']
    if len(otp) !=6:
        return jsonify({'msg':'your OPT is invalid'}),400
    else:
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('''SELECT * FROM signup WHERE email_otp =%s''', [otp])
        verify = my_cursor.fetchone()
        user_id = verify[0]
        now = datetime.datetime.now()
        dt_now = now.strftime("%d-%m-%Y %H:%M:%S")

        if verify:
            my_cursor.execute('''SELECT * FROM signup WHERE id =%s ''', [user_id])
            query = my_cursor.fetchone()
            exp_time = query[7]
            if  dt_now > exp_time:            
                return jsonify({'msg':'your OTP has expired, go back to generate a new otp'})  
            else:
                    return jsonify({'msg':'verfication successful'})  
        else:
            return jsonify({"msg":" Invalid otp check your otp "})
     
# carry = ''.join(map(str, verify))
    #change = str(verify)

@app.route('/api/user/resend_email_otp', methods=['POST'])
@jwt_required()
def resend_email_otp():
        current_user = get_jwt_identity()
        user_email = current_user[2]
        user = str(user_email)
        send = resend_email(user)
           
        return jsonify({'msg':'A new confirmation email has been sent to your email'})


#signin
app.route('/api/user/signin', methods=['POST'])
def signin():
    data = request.json
    phone_number = data['phone_number']
    password = data['password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  signup WHERE phone_number =%s''', [phone_number])
    user = my_cursor.fetchone()
    if user and sha256.verify(password, user[4]):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)
    else:
        return jsonify({'msg':'incorrect password or phone number'}),401  




#password request
@app.route('/api/user/reset_password', methods=['POST'])
def reset_request():
    data = request.json
    email = data['email']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  signup WHERE email =%s''', [email])
    user = my_cursor.fetchone()
    if user is None:
           return jsonify({'msg':'there is no account with that email, you have to signup first'})   
    else:
        mail = forget_password(email)
        return jsonify({'msg':'A link has been sent to your Email to reset your password '})   


#reset the password
@app.route('/api/user/passwordreset/<token>', methods=['POST'])
def passwordreset(token):
    verify=  JWTT.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
    
    if verify is None:
        return jsonify({'msg':'token expired or invalid go back to generate a token to reset your password'}),401  
        
    else:
        email = verify['sub']   
        data = request.json
        password = data['password']
        confirm_password = data['confirm_password']
        if password == confirm_password:
            hash_password = sha256.hash(password)
            my_cursor.execute(f"""UPDATE signup SET password=%s WHERE email = %s""", [hash_password, email])
            mydb.commit()
            return jsonify({'msg':'You password has been reset, you can now login with the new password'}),200  
    return jsonify({'msg':'password and confirm password didn\'t match '}),401  

#account info and update
@app.route('/api/user/account', methods=['GET', 'PUT' ])
@jwt_required()
def account():
        current_user = get_jwt_identity()
        user_id = current_user[0]
        user= "Hi " + current_user[1]
        user_fullname= current_user[1]
        user_email = current_user[2]
        user_phone = current_user[3]
        if request.method == 'GET':
           
            return jsonify({'user':user,
                        'fullname': user_fullname, 
                         'email':user_email,
                         'phone_number': user_phone})

        elif request.method ==  'PUT':           
            data = request.json
            fullname = data['fullname']
            email = data['email']
            phone_number = data['phone_number']
            if len(phone_number) !=14:
                return jsonify({'msg':'Your phone number is invalid'}),400
            else:   
                my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
                my_cursor.execute('''SELECT * FROM  signup WHERE email =%s''', [email])
                user = my_cursor.fetchone()
                if user:
                   return jsonify({'msg':'Email already exits, use another email'}),400
                else:
                    my_cursor.execute('''SELECT * FROM signup WHERE phone_number =%s''', [phone_number])
                    query = my_cursor.fetchone()
                    if query is None:
                          my_cursor.execute('UPDATE signup SET fullname=%s, email=%s, phone_number=%sWHERE id=%s', [fullname, email, phone_number,  user_id ])
                          mydb.commit()           
                          return jsonify({'success': True,'msg':'Your account has be updated'}),200

                    else:           
                        return jsonify({'msg':'Phone number exists, use another phone number'}),400



#change current password
@app.route('/api/user/change_password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user_id = current_user[0]
    data = request.json
    current_password = data['current_password']
    new_password =  data['new_password']
    confirm_password = data['confirm_password']
    my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
    my_cursor.execute('''SELECT * FROM  signup WHERE id =%s''', [user_id])
    user = my_cursor.fetchone()
    if user and sha256.verify(current_password, user[4]):
        if new_password == confirm_password:
             hash_password = sha256.hash(new_password) 
             my_cursor.execute("""UPDATE signup SET password=%s WHERE id = %s""", [hash_password, user_id])
             mydb.commit() 
             return jsonify({'msg':'Password changed successfully'}),200
        else:
            return jsonify({'msg':'Password didn\'t match'})
    else:
        return jsonify({'msg':'Your current password is incorrect'})        




@app.route('/api/user/address', methods=['POST', 'PUT'])
@jwt_required()
def address():
    current_user = get_jwt_identity()
    try:
       user_id = current_user[0]
    except:
        user_id.DoesNotExist
        return jsonify({'msg':'no user'}),404 
    if request.method == 'POST':
        
        data = request.json
        address = data['address']
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('UPDATE signup SET address=%s WHERE id = %s', [address, user_id])
        mydb.commit() 
        return jsonify({'msg':'Your address has be added'})
    elif request.method ==  'PUT':    
        data = request.json
        new_address = data['new_address']
        my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        my_cursor.execute('UPDATE signup SET address=%s WHERE id = %s', [new_address, user_id])
        mydb.commit()
        return jsonify({'msg':'Your address has be updated'})








# if email != user_email:
#                     my_cursor = mydb.cursor(MySQLdb.cursors.DictCursor)
#                     my_cursor.execute('''SELECT * FROM  signup WHERE email =%s''', [email])
#                     user = my_cursor.fetchone()
#                     if user:
#                        return jsonify({'msg':'Email already exits, use another email'}),400
#                 else:
#                     if phone_number != user_phone:
#                         my_cursor.execute('''SELECT * FROM signup WHERE phone_number =%s''', [phone_number])
#                         query = my_cursor.fetchone()
#                         if query:
#                              return jsonify({'msg':'Phone number exists, use another phone number'}),400
#                     else:
#                             my_cursor.execute('UPDATE signup SET fullname=%s, email=%s, phone_number=%sWHERE id=%s', [fullname, email, phone_number,  user_id ])
#                             mydb.commit()           
#                             return jsonify({'success': True,'msg':'Your account has be updated'}),200


# # elif request.method == 'PUT':
if __name__ == '__main__':
    app.run(debug=True)