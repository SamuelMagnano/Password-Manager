# Python localhost ciphered password manager

Since i almost lost access to my spotify account due to my poor password amministration, i decided to code and create my personal localhost password manager. 

For the connection to the database i used ```XAMPP```, but there should not be problems by using something else.

## Database

The database is meant to be a single account ciphered password manager, called password_manager. I defined only one table named ```sites``` with 4 columns:
- ```id```: integer values used for the updates since everything is ciphered and therefore cannot be modified/accessed by searching its value directly
- ```name```: site URL (eg. google.com)
- ```email```: ciphered email
- ```psw```: ciphered password

The database is automatically created and set up the first time you run the code, if it does not already exist.
Here is the SQL statement:
```"CREATE TABLE IF NOT EXISTS password_manager.sites (id INT AUTO_INCREMENT NOT NULL, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, psw VARCHAR(255) NOT NULL, PRIMARY KEY (id, name, email))"```

## Database entries visualization
It is possible to visualiza the entire database by choosing the fifth action ```Database retrieval``` in which i convert it into a ```pandas DataFrame``` before printing it. Using the same action is also possible to save the database as a .csv file to have it either ciphered and deciphered.

## Possible actions
In the code i defined 9 possible actions:
- Exit
- Upload URL/email/password to the Password Manager
- Uplaod a .csv file (must be of the form name,email,psw) into the database
- Generate random password
- Email + Password retrieval from URL
- Database retrieval
- Get URLs and related passwords from email
- Update password given a URL and email
- Delete (URL,email,password) given URL + email


## Encryption/Decryption

For the encryption/decryption part i opted for the ```Fernet module```, a symmetric way of encryption. I could have gone with asymmetric techniques but since this project is meant for a localhost use i find the pair public/private keys unnecessary.

I ensured a better security by making imperative the use of two separated keys: one for the emails and one for the passwords. In this way even if some "intruder" would find one of our keys, they would not be able to see anything clear.

The keys are automatically generated (by pressing ```Enter```) if not inserted in the cmd when required. ***<ins>It is fundamental to save them somewhere as there are no possible ways to retrieve them in order to decypher the database.</ins>***

As expressed in the cmd while running the code, we must insert the key string contained between b'...' as we need to use them as String encoded and not Byte encoded. The correct switches between String/Byte for the encoding of the keys are already inside the code and should be modified with cautions.

***<ins>The keys in the keys.txt file, as the passwords that might be in previous ciphered.csv files, are not my personal ones.</ins>***

## Modules
For the cryptography:
```
pip install fernet
```
For the random password generation:
```
from random import randrange #built-in python module
```
For the URL, email, password validation check
```
pip install regex
```
For the database connection and SQL executions:
```
pip install mysql-connector-python
```
For the printing of the database:
```
pip install pandas
pip install tabulate
```
