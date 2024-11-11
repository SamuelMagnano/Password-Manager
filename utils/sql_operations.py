import re

import mysql.connector
import pandas as pd
from mysql.connector import Error

# from pandas import DataFrame
from tabulate import tabulate


# database initialization
# if the db doesn't exists then create it, otherwise nothing
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
                csr.execute("CREATE TABLE IF NOT EXISTS password_manager.sites (id INT AUTO_INCREMENT NOT NULL, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, psw VARCHAR(255) NOT NULL, PRIMARY KEY (id, name, email))")
                print("Table sites created")
            except Error as _:
                print("Password Manager database already in localhost") 
            csr.close()
            db.close()
            print("Connection closed")
        else:
            print()
            print("Cannot open connection to the database!\n")
    except Error as e:
        print(f"Error: {e}")

# since i upload crypted emails and passwords and i don't want to have the a site with the email that i'm trying to insert more that 1 time
# i need to retireve all the emails linked to a specific site, decrypt them and check if the email i am trying to insert is not in this list
def upload(cipher,url,email,psw):
    #site url check
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("URL not valid. Insert a valid one: ")
    #email check
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
    #password check
    while not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",psw):
        psw = input("Password not valid. It must contain an upper case, lower case, a number, a special character and be long between 8/16 characters.\
                    \nInsert a valid one: ")
    encripted_email,encripted_psw = cipher.encryption(email,psw)
    
    
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
                encripted_emails_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i want to insert
                for element in encripted_emails_list:
                    element = cipher.email_decryption(element[0])
                    #if -1 it means that the key we used is wrong so we should't upload anything
                    if element == email or element == -1: 
                        #the error print is in the cipher part of the decription
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
            #decode because i need to pass it as a string and not byte
            csr.execute("INSERT INTO sites (name, email, psw) VALUES (%s,%s,%s)", (url,encripted_email.decode('utf-8'),encripted_psw.decode('utf-8')))
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


# Download the whole db (id,name,email,psw), for each entry to upload check if the tuple (name,email) is already inside the db with a different password.
# If yes, append the tuple (name,email,password) to the possible_uploads list
# Nothing otherwise

# The second check to do is for the entries that do no appear in the db (name,email) != to all (name,email) in the db
# If there are any add them to the insert_into
# Nothing otherwise
def upload_unciphered_csv(cipher):
    path = str(input("Drag and drop the .csv file here: "))
    csv_df = pd.read_csv(path)

    db_df = db_to_dataframe(cipher)
    #print(tabulate(db_df, headers='keys', tablefmt='fancy_grid', showindex=False))

    merged_df = csv_df.merge(db_df, on=["name", "email"], suffixes=('_csv', '_db'))
    # Filter rows where the passwords are different (the new password is on position 2 with column named "password_csv")
    possible_updates = merged_df[merged_df["password_csv"] != merged_df["password_db"]]

    # indicator tells me if the pair name,email appears on the left_only dataframe, the right-only or both. I'm interested in the rows that appear in the left only since they are from csv_df
    merged_df = csv_df.merge(db_df, on=["name", "email"], suffixes=("","_db"), how="outer", indicator=True)
    insert_into = merged_df[merged_df["_merge"] == "left_only"]
    print("\nUnique rows to be inserted into the database:")
    print(tabulate(insert_into[["name","email","password"]], headers="keys", tablefmt="fancy_grid", showindex=False))

    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        # db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            # trying to insert one row of a time, the whole dataframe inside the database
            try:
                for element in insert_into.itertuples(index=False):
                    # check if url, email, password are valid
                    if re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",element[0]) and \
                        re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",element[1]) and \
                        re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",element[2]):
                        print(f"Inserting, if url + email not in the database, URL: {element[0]}, email: {element[1]}, password: {element[2]}")
                        # i need to cipher email and password since in the csv are not ciphered
                        csr.execute("INSERT INTO sites (name, email, psw) VALUES (%s,%s,%s)", (element[0],cipher.email_encryption(element[1]).decode('utf-8'),cipher.psw_encryption(element[2]).decode('utf-8')))
                    else:
                        print(f"Invalid entry! URL: {element[0]}, email: {element[1]}, password: {element[2]}. At least one of the inputs is not valid!")
                db.commit()
                if possible_updates.empty == False:
                    print("\nPossible updates:")
                    print(tabulate(possible_updates, headers="keys", tablefmt="fancy_grid", showindex=False))
                    response = input("\nThese URL + email from the .csv files are already in the database with a DIFFERENT password, do you want to update them ? [y,n]: ").lower()
                    if response in [""," ","y","yes"]:
                        for element in possible_updates.itertuples(index=False):
                            if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",element[2]):
                                update_psw(cipher,url=element[0],email=element[1],psw=element[2])
                            else: print(f"Entry not updated, password not valid! URL: {element[0]} email: {element[1]} password: {element[2]}")
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
        

# Decipher the ciphered .csv in order to check if there are entries to insert into the database or to just update the their passwords
def upload_ciphered_csv(cipher):
    path = str(input("Drag and drop the .csv file here: "))
    cifered_csv_df = pd.read_csv(path)
    deciphered_csv_df = pd.DataFrame(columns=["name", "email", "password"])
    
    # deciphering the .csv
    try:
        for element in cifered_csv_df.itertuples(index=False):
            original_email,original_password = cipher.decryption(element[1],element[2])
            if original_email != -1 and original_password != -1:
                deciphered_csv_df = deciphered_csv_df._append({"name": element[0], "email": original_email, "password": original_password}, ignore_index=True)
        
        db_df = db_to_dataframe(cipher)
        #print(tabulate(db_df, headers='keys', tablefmt='fancy_grid', showindex=False))

        merged_df = deciphered_csv_df.merge(db_df, on=["name", "email"], suffixes=('_csv', '_db'))
        # Filter rows where the passwords are different (the new password is on position 2 with column named "password_csv")
        possible_updates = merged_df[merged_df["password_csv"] != merged_df["password_db"]]

        # indicator tells me if the pair name,email appears on the left_only dataframe, the right-only or both. I'm interested in the rows that appear in the left only since they are from csv_df
        merged_df = deciphered_csv_df.merge(db_df, on=["name", "email"], suffixes=("","_db"), how="outer", indicator=True)
        insert_into = merged_df[merged_df["_merge"] == "left_only"]
        print("\nUnique rows to be inserted into the database:")
        print(tabulate(insert_into[["name","email","password"]], headers="keys", tablefmt="fancy_grid", showindex=False))

        try:
            db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
            # db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
            if db.is_connected():
                print("\nConnection to database opened")
                csr = db.cursor()
                # trying to insert one row of a time, the whole dataframe inside the database
                try:
                    for element in insert_into.itertuples(index=False):
                        # check if url, email, password are valid
                        if re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",element[0]) and \
                            re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",element[1]) and \
                            re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",element[2]):
                            print(f"Inserting, if url + email not in the database, URL: {element[0]}, email: {element[1]}, password: {element[2]}")
                            # i need to cipher email and password since in the csv are not ciphered
                            csr.execute("INSERT INTO sites (name, email, psw) VALUES (%s,%s,%s)", (element[0],cipher.email_encryption(element[1]).decode('utf-8'),cipher.psw_encryption(element[2]).decode('utf-8')))
                        else:
                            print(f"Invalid entry! URL: {element[0]}, email: {element[1]}, password: {element[2]}. At least one of the inputs is not valid!")
                    db.commit()
                    if possible_updates.empty == False:
                        print("\nPossible updates:")
                        print(tabulate(possible_updates, headers="keys", tablefmt="fancy_grid", showindex=False))
                        response = input("\nThese URL + email from the .csv files are already in the database with a DIFFERENT password, do you want to update them ? [y,n]: ").lower()
                        if response in [""," ","y","yes"]:
                            for element in possible_updates.itertuples(index=False):
                                if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",element[2]):
                                    update_psw(cipher,url=element[0],email=element[1],psw=element[2])
                                else: print(f"Entry not updated, password not valid! URL: {element[0]} email: {element[1]} password: {element[2]}")
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
    except Error as e:
        #the deciphering exception is handled in the deciphering  
        print()

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
                #decrypting the emails and passwords
                for element in tuples_list:
                    original_email,original_password = cipher.decryption(element[0],element[1])
                    if original_email == -1 or original_password == -1:
                        #the error print is in the cipher part of the decription
                        break
                    else:
                        print(f"\nEmail: {original_email}")
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


def get_site_psw_from_email(cipher,email):
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get whole database and then process the result
            try:
                csr.execute("SELECT name,email,psw FROM sites")
                print("Whole database retrieved. Decripting the emails to obtain the linked site + password")
                tuples_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i requested
                for element in tuples_list:
                    original_email,original_password = cipher.decryption(element[1],element[2])
                    if original_email == -1 or original_password == -1:
                        #the error print is in the cipher part of the decription
                        break
                    elif original_email == email:
                        print(f"\nUrl:{element[0]}")
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
    ciphered_database,deciphered_database = pd.DataFrame(columns=["name", "email", "password"]),pd.DataFrame(columns=["name", "email", "password"])
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        #trying to connect to db
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT name,email,psw FROM sites")
                print("Database retrieval and decription")
                whole_database = csr.fetchall()
                #decrypting the emails and passwords and adding them to the DataFrames
                for element in whole_database:
                    original_email,original_password = cipher.decryption(element[1],element[2])
                    if original_email == -1 or original_password == -1:
                        #the error print is in the cipher part of the decription
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
    deciphered_database = deciphered_database.sort_values(by=['name'])
    ciphered_database = ciphered_database.sort_values(by=['name'])
    print(tabulate(deciphered_database, headers='keys', tablefmt='fancy_grid', showindex=False))
    if response in [""," ","y","yes"]:
        deciphered_database.to_csv('deciphered_database.csv', index=False, mode='w')
        print("\nciphered_dat.csv created/updated!")
        ciphered_database.to_csv('ciphered_database.csv', index=False, mode='w')
        print("ciphered_database.csv created/updated!")


def db_to_dataframe(cipher):
    ciphered_database,deciphered_database = pd.DataFrame(columns=["name", "email", "password"]),pd.DataFrame(columns=["name", "email", "password"])
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        #trying to connect to db
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT name,email,psw FROM sites")
                print("Database retrieval and decription")
                whole_database = csr.fetchall()
                #decrypting the emails and passwords and adding them to the DataFrames
                for element in whole_database:
                    original_email,original_password = cipher.decryption(element[1],element[2])
                    if original_email == -1 or original_password == -1:
                        #the error print is in the cipher part of the decription
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
    return deciphered_database.sort_values(by=['name'])

# To make the delete work without downloading the whole db, deleting the single row i specified and reupload everything,
# i had to add an id as a primary key auto-increment in the database.
# The problem is that since i store my emails ciphered i cannot delete that row easily since a key can cipher in several ways the same string
def delete(cipher,url,email):
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("URL not valid. Insert a valid one: ")
    #email check
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
        
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT id,name,email FROM sites WHERE name = (%s)", ((url,)))
                print(f"{url} rows retrieved. Decripting the emails to delete the specified one")
                tuples_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i requested
                for element in tuples_list:
                    original_email = cipher.email_decryption(element[2])
                    if original_email == -1:
                        #the error print is in the cipher part of the decription
                        break
                    elif original_email == email:
                        csr.execute("DELETE FROM sites WHERE id = (%s)", ((element[0],)))
                        db.commit()
                        print(f"Deleted URL:{element[1]} email: {original_email} from password_manager!")
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

def update_psw(cipher,url,email,psw):
    while not re.match(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/[\w\.-]*)*/?$",url):
        url = input("URL not valid. Insert a valid one: ")
    #email check
    while not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$",email):
        email = input("Email not valid. Insert a valid one: ")
    while not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",psw):
        psw = input("Password not valid. It must contain an upper case, lower case, a number, a special character and be long between 8/16 characters.\
                    \nInsert a valid one: ")
        
    try:
        db = mysql.connector.MySQLConnection(host="localhost", user="root", database="password_manager", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print("\nConnection to database opened")
            csr = db.cursor()
            #get emails+psw from URL
            try:
                csr.execute("SELECT id,email FROM sites WHERE name = (%s)", ((url,)))
                print(f"{url} rows retrieved. Decripting the emails to update the password of the specified one")
                tuples_list = csr.fetchall()
                #decrypting the emails and checking if any of them are the same as the one i requested
                for element in tuples_list:
                    original_email = cipher.email_decryption(element[1])
                    if original_email == -1:
                        #the error print is in the cipher part of the decription
                        break
                    elif original_email == email:
                        encripted_psw = cipher.psw_encryption(psw)
                        csr.execute("UPDATE sites SET psw=(%s) WHERE id = (%s)", (encripted_psw.decode('utf-8'), element[0])) #decode because i need to pass it as a string and not byte
                        print(f"Updated URL:{url} email: {email} from password_manager!")
                db.commit()
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