from classes import sql_operations,crypto

if __name__ == "__main__":
  cycle_condition = True
  sql_operations.initialization()
  print("If you are already in possess of a cipher keys (Fernet key) just insert the value in between b'...'")
  cipher = crypto.Cipher(input("Insert email_key: "),input("insert psw_key: "))
  
  #doable operations
  while cycle_condition:
    option = input("Choose an option\n 1.Upload name/email/psw\n").lower()
    match int(option):
      case 1:
        sql_operations.upload(cipher,str(input("\nSite Name: ")),str(input("Email: ")),str(input("Password: ")))
        cycle_condition = False