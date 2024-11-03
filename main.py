from utils import sql_operations,crypto

if __name__ == "__main__":
  cycle_condition = True
  sql_operations.initialization()
  print("If you are already in possess of a cipher keys (Fernet key) just insert the value in between b'...'")
  cipher = crypto.Cipher(input("Insert email_key: "),input("insert psw_key: "))
  
  print("Here is the list of doable operations:\n0. Exit\n1. Upload name/email/password to the Password Manager\n2. Generate random password")
  while cycle_condition:
    option = input("\nChoose an option: ").lower()
    match int(option):
      #Exit
      case 0: cycle_condition = False
      #Upload
      case 1:
        sql_operations.upload(cipher,str(input("\nSite Name: ")),str(input("Email: ")),str(input("Password: ")))
      #psw generation
      case 2: 
        password = cipher.random_psw()
        print(password)