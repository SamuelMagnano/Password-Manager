from cryptography.fernet import Fernet 
from random import randrange
import re

class Cipher:
  #keys generation if not correct (memorization as long as the main process is alive)
  def __init__(self,email_key,psw_key):
    inside = False
    #i have an error in a key the moment it is equals to the other or its length is not equal to 44 (Fernet key length)
    while email_key == psw_key or len(email_key)!=44 or len(psw_key)!=44:
      inside = True
      email_key = Fernet.generate_key()
      psw_key = Fernet.generate_key()
    print(f"\nemail_key: {email_key}\npsw_key: {psw_key}\n")
    #i need to do it otherwise i might encode an already encoded string (Fernet returns encoded keys)
    if inside == True:
      self.email_key = email_key
      self.psw_key = psw_key
    else:
      self.email_key = email_key.encode('utf-8')
      self.psw_key = psw_key.encode('utf-8')

  #16 characters random password generator
  def random_psw(self):
    cond = False
    while not cond:
      allowed_characters = [
      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
      'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
      '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
      '[', ']', '{', '}', '|', ';', ':', "'", ',', '<', '.', '>', '/', '?']
      psw = ""
      for _ in range(0,16):
        #randrange(n) gives a random integer in the range [0,n-1] 
        psw = psw + allowed_characters[randrange(len(allowed_characters))]
      if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,16}$",psw): 
        cond = True
    return psw

  #email and password encryption
  def encryption(self,email,psw):
    f_email = Fernet(self.email_key)
    f_psw = Fernet(self.psw_key)
    encrypted_email = f_email.encrypt(email.encode('utf-8'))
    encrypted_psw = f_psw.encrypt(psw.encode('utf-8'))
    print(f"\nCripted email:{encrypted_email}\nCripted psw:{encrypted_psw}\n")
    return encrypted_email,encrypted_psw

  #email and password decryption
  def decryption(self,encrypted_email,encrypted_psw):
    try:
      f_email = Fernet(self.email_key)
      f_psw = Fernet(self.psw_key)
      original_email = f_email.decrypt(encrypted_email).decode() #decrypt deciphers while decode converts bytes to string, otherwise i would have b' at the start of the string
      original_psw = f_psw.decrypt(encrypted_psw).decode()
      #print(f"\nDecripted email: {original_email}\nDecripted psw: {original_psw}\n")
      return original_email,original_psw
    except:
      print("The key used is not the correct one the decryption!")
      #i guess i could raise an error and let it be handled by the caller but i'm not sure if it is possible in python
      return -1,-1
  
    #email and password decryption
  def email_decryption(self,encrypted_email):
    try:
      f_email = Fernet(self.email_key)
      original_email = f_email.decrypt(encrypted_email).decode() #decrypt deciphers while decode converts bytes to string, otherwise i would have b' at the start of the string
      #print(f"\nDecripted email: {original_email}")
      return original_email
    except:
      print("The key used is not the correct one the decryption!")
      return -1