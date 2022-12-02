from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os
import MySQLdb.cursors
import mysql.connector
import MySQLdb.cursors

from flask_jwt_extended import (JWTManager, create_access_token, get_jwt_identity,
                                 jwt_required, get_jwt)

ACCESS_EXPIRES = timedelta(hours=1)                                 

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:''@localhost/foodapi'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

jwt = JWTManager(app)

mydb = mysql.connector.connect(
    host='localhost',
    user ='root',
    password ='',
    database ='foodapi',
    )

my_cursor =mydb.cursor(buffered=True)  