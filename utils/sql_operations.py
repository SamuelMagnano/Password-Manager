import mysql.connector
from mysql.connector import Error
import re

#database initialization
#if the db doesn't exists then create it, otherwise nothing 
def initialization():
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print()
            print("Connection to database opened")
            csr = db.cursor()
            #attempt to create the database
            try:
                csr.execute("CREATE DATABASE password_manager")
                print("password_manager database created")
                #if everything goes right i then create the main and only table sites (name,email,psw)
                #TODO vedi se serve rendere email e psw TEXT, quindi 16mila caratteri, invece di VARCHAR(255)
                csr.execute("CREATE TABLE IF NOT EXISTS password_manager.sites (name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, psw VARCHAR(255) NOT NULL,PRIMARY KEY (name, email))")
                print("Table sites created")
            except Error as already_exists:
                print("Password Manager database already in localhost") 
            csr.close()
            db.close()
            print("Connection closed\n")
        else:
            print()
            print("Cannot open connection to the database!\n")
    except Error as e:
        print(f"Error: {e}")
            
def upload(cipher,url,email,psw):
    #site url check
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("Site address not valid. Insert a valid one: ")
    #email check
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
    cipher.encryption(email,psw)
    #TODO fare la INSERT INTO dei valori restituiti dopo l'encoding (ti arrivano come stringa e non come bytes)