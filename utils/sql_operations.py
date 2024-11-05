import mysql.connector
from mysql.connector import Error
import re
from pandas import DataFrame

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
            print("Connection closed")
        else:
            print()
            print("Cannot open connection to the database!\n")
    except Error as e:
        print(f"Error: {e}")

#since i upload crypted emails and passwords and i don't want to have the a site with the email that i'm trying to insert more that 1 time
#i need to retireve all the emails linked to a specific site, decrypt them and check if the email i am trying to insert is not in this list
def upload(cipher,url,email,psw):
    #site url check
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("URL not valid. Insert a valid one: ")
    #email check
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
    while not re.match(r"^[\w!@#$%^&*()\-_=+[\]{}|;:'\",.<>?/]{1,16}$",psw):
        psw = input("Password not valid. Insert a valid one: ")
    encrypted_email,encrypted_psw = cipher.encryption(email,psw)
    
    insert_condition = True
    #try to open connection to database
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #obtaining the emails linked to an URL
            try:
                csr.execute("SELECT email FROM sites WHERE name = (%s)", ((url,)))
                print("Checking if the email is already in the database for the given URL")
                encrypted_emails_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i want to insert
                for element in encrypted_emails_list:
                    element = cipher.email_decryption(element[0])
                    #if -1 it means that the key we used is wrong so we should't upload anything
                    if element == email or element == -1: 
                        insert_condition = False
                        break
            except Error as e:
                print("An error occurred and the operation has not been executed. Try again.") 
                print(e)
        else:
            print("\nCannot open connection to the database!\n")
            insert_condition = False
    except Error as e:
        print(f"Error: {e}")
        insert_condition = False
    
    if insert_condition == True:
        print(f"The email: {email} has never been linked to the site: {url}")
        #if i get here the connection is still open so i don't need to open it again but i must close it
        try:
            csr.execute("INSERT INTO sites (name, email, psw) VALUES (%s,%s,%s)", (url,encrypted_email.decode('utf-8'),encrypted_psw.decode('utf-8')))
            print("Site, Email, Password inserted into the database")
            db.commit()
        except Error as e:
            print("An error occurred and the operation has not been executed. Try again.") 
            print(e)
        csr.close()
        db.close()
        print("Connection closed")
    else:
        if element!=-1: print("Email already inside the database for the given URL!\nDelete the already existing one or update it.")
        

def get_email_psw_from_url(cipher,url):
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("URL not valid. Insert a valid one: ")
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT email,psw FROM sites WHERE name = (%s)", ((url,)))
                print("Crypted emails and passwords retrieved and ready to be decrypted.")
                tuples_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i want to insert
                for element in tuples_list:
                    original_email,original_password = cipher.decryption(element[0],element[1])
                    if original_email == -1 or original_password == -1:
                        break
                    else:
                        print(f"Email: {original_email}")
                        print(f"Password: {original_password}")
            except Error as e:
                print("An error occurred and the operation has not been executed. Try again.")
                print(e)
            csr.close()
            db.close()
            print("Connection closed")
        else:
            print("\nCannot open connection to the database!\n")
    except Error as e:
        print(f"Error: {e}")
        
    
def db_retrieval(cipher,response):
    ciphered_database,deciphered_database = DataFrame(columns=["name", "email", "password"]),DataFrame(columns=["name", "email", "password"])
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        #trying to connect to db
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT * FROM sites")
                print("Database retrieval and decription")
                whole_database = csr.fetchall()
                #decrypting the emails and passwords and adding them to the DataFrame
                for element in whole_database:
                    original_email,original_password = cipher.decryption(element[1],element[2])
                    if original_email == -1 or original_password == -1:
                        break
                    else:
                       deciphered_database = deciphered_database._append({"name": element[0], "email": original_email, "password": original_password}, ignore_index=True)
                       ciphered_database = ciphered_database._append({"name": element[0], "email": element[1], "password": element[2]}, ignore_index=True)
            except Error as e:
                print("An error occurred and the operation has not been executed. Try again.")
                print(e)
            csr.close()
            db.close()
            print("Connection closed")
        else:
            print("\nCannot open connection to the database!\n")
    except Error as e:
        print(f"Error: {e}")
    print()
    print(deciphered_database.sort_values(by=['name']).to_string(index=False))
    if response in [""," ","y","yes"]:
        deciphered_database.to_csv('deciphered_database.csv', index=False)
        print("\nciphered_dat.csv created/updated")
        ciphered_database.to_csv('ciphered_database.csv', index=False)
        print("ciphered_database.csv created/updated")