[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/7aciRwH2)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-718a45dd9cf7e7f842a935f5ebbe5719a5e09af4491e668f4dbf3b35d5cca122.svg)](https://classroom.github.com/online_ide?assignment_repo_id=13544316&assignment_repo_type=AssignmentRepo)
# Frappster BANK (CLI)  
This might sound crazy but it's the truth- I own a bank

### Setup (only if you above 169)
**idk how y'll start virtual env on windows...** 
I guess install it all globaly...then
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

## for noobs (Tutorial)
There is an test.db with some populated Users and asigned accounts to
them.
If you delete db on start it will anyways create 
the super powerfull Wizard Anorak (aka admin account) otherwise there is
no way to use it (it's a bank after all it gotta be properly secured...)

then you can log in with his superpowerfull credentials
login ID: 42069
password: secure

There are other prebuilt users with prebuilt accounts and some
transaction history to see. (P.S. only admins and employees can create
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

But on the bright side:
1) auto completion with tab - check
1) deposit - check
2) witdhrawl - check
3) wire transfer - check 
4) Some what rolle based acces - check
5) SECUIRITY - shrek


### There is more backend logic...
Not everything is implemented yet.
Role based access works fine.
But there is also granular permissions based access.
For diffrent types of Employeess for example.
No logging is implemented so if smth goes wrong wrong, welp woopsie you
won't know what. Neither Audit logs are built so if some Jeff deletes
Joe (which he can't as there is no delete UI funcionality) nobody will
know who did that.
