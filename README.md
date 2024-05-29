# Frappster BANK (CLI)  
This might sound crazy but it's the truth- I own a bank

### Setup 
```bash
py -m venv venv
source venv/bin/activate
pip install -r requirments.txt
py main.py
```
or run it as an module from root dir:
```bash
py -m frappster.main
```

## Usage 
There is an test.db with some pre-populated Users  with assigned accounts.

If you delete db before start. No worries, it will create 
the super powerfull Wizard Anorak (aka admin account) otherwise there is
no way to use it (it's a bank after all it gotta be properly secured...)

Then you can log in with his superpowerfull and secure credentials
login ID: 42069
password: secure

User accounts with some transaction history to test CLI.
(P.S. only admins and employees can create
users and open accounts for chosen users)

First Customer User:
login ID: 700739
password: 123

Account number: 643869

Second Customer User (yeah high secuirity this guys password is an empty
string):
login ID: 388667
password: 

His savings account number: 616269

And lastly an Employee User (he cannot create new admins but he can
create Customer users and assign them accounts)
login ID: 736559
password: 123

## Features 
But on the bright side:
1) auto completion with tab - check
1) deposit - check
2) witdhrawl - check
3) wire transfer - check 
4) Some what rolle based acces - check
5) SECUIRITY - shrek


### There is more backend logic...
Not everything is implemented yet.
Role based access works fine,
but there is also granular permissions based access.
For different types of Employeess for example.
No logging is implemented so if smth goes wrong wrong, welp woopsie you
won't know what. Neither Audit logs are built so if some Jeff deletes
Joe (which he can't as there is no delete UI funcionality) nobody will
know who did that.
