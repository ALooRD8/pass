import string
import sys
import random
import clipboard
from cs50 import SQL

R = "\033[1;31m"
W = "\033[0;37m"
Y = "\033[1;33m"
W2 = "\033[1;37m"

def delete_multiple_lines(n=1):
    """Delete the last line in the STDOUT."""
    for _ in range(n):
        sys.stdout.write("\x1b[1A")  # cursor up one line
        sys.stdout.write("\x1b[2K")

def gen():
    '''
    generate the password and return the id of the password 
    '''
    s1 = list(string.ascii_lowercase)
    s2 = list(string.ascii_uppercase)
    s3 = list(string.digits)
    s4 = list(string.punctuation)

    inputQ = input("How many numbers do you want: ")

    while True:
        try:
            inputQ = int(inputQ)
            if inputQ < 8:
                print(f"{R}Please put alot of numbers{W}")
                inputQ = input("How many numbers do you want: ")
            else:
                break
        except:
            print(f"{R}Pleaes put just numbers{W}")
            inputQ = input("Please put numbers: ")


    password = []


    random.shuffle(s1)
    random.shuffle(s2)
    random.shuffle(s3)
    random.shuffle(s4)

    part1 = round(inputQ * 30/100)
    part2 = round(inputQ * 20/100)

    for i in range(part1):
        password.append(s1[i])
        password.append(s2[i])

    for i in range(part2):
        password.append(s3[i])
        password.append(s4[i])

    random.shuffle(password)

    password = "".join(password[0:])
    input_q = input("Put The name of link: ")
    print(password)
    db = dba()
    try:
        id = db.execute("INSERT INTO password (pass, web_name) VALUES(?, ?)", password, input_q)
    except:
        print(f"{R}There was an error please try again{W}")
    clipboard.copy(password)
    return id

def main():
    open("passwords.db", "a+").close()
    create()
    j = 8
    for i in range(3):
        try:
            print(f"\n{W2}1.New password{W}\n{Y}2.Show the old passwords{W}\n{W2}3.Show specific passwords{W}\n{Y}4.Delete specific password{W}\n{W2}5.More...{W}\n")
            input_q = int(input(""))
            delete_multiple_lines(j)
            if input_q == 1:
                trans(1)
                break
            elif input_q == 2:
                show()
                break
            elif input_q == 3:
                show(2)
                break
            elif input_q == 4:
                delete()
                break
            elif input_q == 5:
                main2()
                break
        except ValueError:
            delete_multiple_lines(8 + i)
            print(f"{R}Invalid Value{W}")
            if i == 2:
                delete_multiple_lines()

def main2():
    j = 6
    for i in range(3):
        try:
            print(f"\n{Y}1.Create a new email{W}\n{W2}2.Delete an email{W}\n{Y}3.Create a manual password{W}\n")
            inp = int(input(""))
            delete_multiple_lines(j)
            if inp == 1:
                email()
                break
            elif inp == 2:
                deleteEmail()
                break
            elif inp == 3:
                trans(0)
                break
        except ValueError:
            delete_multiple_lines(6 + i)
            print(f"{R}Invalid Value{W}")
            if i == 2:
                delete_multiple_lines()

def trans(mode):
    '''
    mode 2 for return the select id from accounts
    any mode else for insert the acc_id and pass_id to acc_pass 
    '''
    print("\nWhich account will you choose")
    db = dba()
    row = db.execute("SELECT * FROM accounts")
    pr(row, mode=2)
    try:
        inp = int(input(""))
        if inp >= row[0]["id"] and inp <= row[-1]["id"]:
            delete_multiple_lines(len(row) + 3)
            if mode == 2:
                print("#" * 44)
                return inp
            elif mode == 0:
                id = createPassManual()
                db.execute("INSERT INTO acc_pass (account_id, password_id) VALUES(?, ?)", inp, id)
            else:
                id = gen()
                db.execute("INSERT INTO acc_pass (account_id, password_id) VALUES(?, ?)", inp, id)
    except ValueError:
        print(f"{R}Invalid Value{W}")

def show(mode=1):
    '''
    mode 1 for show the pass and web_name from password
    mode 3 for show all from password
    any mode else for show specific pass and web_link from password
    '''
    db = dba()
    # the id of account
    id = trans(2)
    if mode == 1:
        row = db.execute("SELECT pass, web_name FROM password WHERE id IN (SELECT password_id FROM acc_pass WHERE account_id = ?)", id)
        pr(row)
    elif mode == 3:
        row = db.execute("SELECT * FROM password WHERE id IN (SELECT password_id FROM acc_pass WHERE account_id = ?)", id)
        pr(row, mode=3)
    else:
        try:
            inp = input("")
            row = db.execute(f'SELECT pass, web_name FROM password WHERE id IN (SELECT password_id FROM acc_pass WHERE account_id = ?) AND web_name LIKE "%{inp}%";', id)
            pr(row)
        except RuntimeError:
            pass

def email():
    db = dba()
    inp = input("\nWrite the email: ")
    db.execute("INSERT INTO accounts (account) VALUES(?)", inp)

def create():
    try:
        db = dba()
        db.execute("CREATE TABLE accounts (id INTEGER,account TEXT,PRIMARY KEY (id))")
        db.execute("CREATE TABLE password (id INTEGER,pass TEXT,web_name TEXT,PRIMARY KEY (id))")
        db.execute("CREATE TABLE acc_pass (account_id INTEGER,password_id INTEGER,FOREIGN KEY (account_id) REFERENCES accounts(id),FOREIGN KEY (password_id) REFERENCES password(id))")
    except:
        pass

def createPassManual():
    db = dba()
    passInp = input("Put the password: ")
    linkInp = input("Put the link: ")
    id = db.execute("INSERT INTO password (pass, web_name) VALUES(?, ?)", passInp, linkInp)
    clipboard.copy(passInp)
    return id 

def delete():
    db = dba()
    show(3)
    inp = input("")
    db.execute("DELETE FROM acc_pass WHERE password_id = ?", inp)
    db.execute("DELETE FROM password WHERE id = ?", inp)
    print()

def deleteEmail():
    db = dba()
    # the id of the account
    id = trans(2)
    delete_multiple_lines()
    db.execute("DELETE FROM acc_pass WHERE account_id = ?", id)
    db.execute("DELETE FROM password WHERE id IN (SELECT password_id FROM acc_pass WHERE account_id = ?)", id)
    db.execute("DELETE FROM accounts WHERE id = ?", id)

def dba():
    return SQL("sqlite:///passwords.db")

def pr(row, mode=1) -> None:
    '''
    mode 1 for print the pass and the web_name from password
    mode 3 for print the id and the pass and the web_name from password
    any mode else for print the id and the account from accounts 
    '''
    if mode == 1:
        for i in range(len(row)):
            print(row[i]["pass"], (" " * (20 - len(row[i]["pass"]))), "| ", row[i]["web_name"])
        if len(row) == 1:
            clipboard.copy(row[0]["pass"])
    elif mode == 3:
        for i in range(len(row)):
            if row[i]["id"] < 10:
                print(row[i]["id"], "| ", row[i]["pass"], (" " * (20 - len(row[i]["pass"]))), "| ", row[i]["web_name"])
            else:
                print(str(row[i]["id"])+ "| ", row[i]["pass"], (" " * (20 - len(row[i]["pass"]))), "| ", row[i]["web_name"])
    else:
        for i in range(len(row)):
            print(row[i]["id"], "|", row[i]["account"])
        print()

if __name__ == "__main__":
    main()