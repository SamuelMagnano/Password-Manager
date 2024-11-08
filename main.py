from utils import sql_operations,crypto

if __name__ == "__main__":
  cycle_condition = True
  sql_operations.initialization()
  print("\nIf you are already in possess of a cipher keys (Fernet key) just insert the value in between b'...'")
  cipher = crypto.Cipher(input("Insert email_key: "),input("insert psw_key: "))
  
  print("Here is the list of doable operations:\
        \n0. Exit\
        \n1. Upload URL/email/password to the Password Manager\
        \n2. Generate random password\
        \n3. Email + Password retrieval from URL\
        \n4. Database retrieval\
        \n5. Get URLs and related passwords from email\
        \n6. Update password given a URL and email\
        \n7. Delete (URL,email,password) given URL + email")
  while cycle_condition:
    option = input("\nChoose an option: ")
    match int(option):
      #Exit
      case 0: cycle_condition = False
      #Upload
      case 1:
        sql_operations.upload(cipher,str(input("\nURL: ")),str(input("Email: ")),str(input("Password: ")))
      #psw generation
      case 2: 
        password = cipher.random_psw()
        print(password)
      #email+psw retrieval from site
      case 3:
        sql_operations.get_email_psw_from_url(cipher,str(input("\nURL: ")))
      #database retrieval
      case 4:
        sql_operations.db_retrieval(cipher,str(input("Do you want to save the database as a .csv [y/n]: ")))
      #Get sites and related passwords from email
      case 5:
        sql_operations.get_site_psw_from_email(cipher,str(input("Email: ")))
      #update password given URL + email 
      case 6:
        sql_operations.update_psw(cipher,str(input("\nURL: ")),str(input("Email: ")),str(input("New password: ")))
      #Delete a row in the database from URL + email
      case 7:
        sql_operations.delete(cipher,str(input("\nURL: ")),str(input("Email: ")))