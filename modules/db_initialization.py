import mysql.connector
from mysql.connector import Error
from datetime import datetime

def db_initialization():
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="", port=3306) #if you are using XAMPP
        #db = mysql.connector.MySQLConnection(host="localhost", database="password_manager", user="root", password="admin", port=3306) if you are using MySQL wokbench
        if db.is_connected():
            print(current_time,"Connection opened")
            csr = db.cursor()
            csr.close()
            db.close()
            current_time = datetime.now().strftime("%H:%M:%S")
            print(current_time,"Connection closed")
        else:
            print("Cannot open connection to the database!")
    except Error as e:
        print(f"Error: {e}")