#Import Classes
import json
import os
import random
from datetime import datetime, date
from Account import Account
from Reccomendation import Reccomendation


#Retrieve data from json file
DATA_FILE = "accounts.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {"identities": {}, "accounts": {}}
    

#Save accounts as dictionaries
def save_data(identities, accounts):
    accounts_dict = {}
    for acc_id, acc in accounts.items():
        accounts_dict[acc_id] = acc.acc_to_dict()
    data = {"identities": identities, "accounts": accounts_dict}
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

#Load data in from json and make usable
data = load_data()
identity_dir = data["identities"]
account_dir = {}
for acc_id, acc_data in data["accounts"].items():
    account_dir[acc_id] = Account.dict_to_acc(acc_data)


#Create Account Function
def create_or_login():
    name = input("Welcome! Please enter your name: ").strip().upper()
    if name in identity_dir:
        id_num = ''
        while True:
            id_num = input("Please enter you account number: ")
            if id_num != identity_dir[name]:
                print("Account number incorrect. Please try again.")
            else:
                break
        account = account_dir[id_num]
    else:
        answer = input("You do not have an account. Would you like to create one? ")
        if answer.upper().strip() == "YES":
            while True:
                id_num = str(random.randint(100_000_000, 999_999_999))
                if id_num not in identity_dir.values():
                    break
            identity_dir[name] = id_num
            account = Account(name, id_num)
            account_dir[id_num] = account
            print(f"Account created! Your account number is {id_num}.")
            save_data(identity_dir, account_dir)
        else:
            print("Returning to login screen...")
            return None
    return account

#Call summarize function and print
def summarize_account(account):
    print(account.summarize())


#Call deposit instance and ensure all inputs are valid
def deposit_funds(account):
    amount = input("Please enter the amount depositted: $")    
    while True:
        try:
            amount = float(amount)
            break
        except ValueError:
            amount = input("Please enter a valid amount: $")
    account.add_amount(amount)
    save_data(identity_dir, account_dir)
    print(f"Your account balance is now ${account.balance:.2f}.")


#Call bill instance and ensure all inputs are valid
def create_bill(account):
    bill_name = input("Please enter the bill name: ")
    bill_amount = input("Please enter the bill amount: ")
    recurring = input("Is this bill recurring? (Y/N)")
    rec_freq = 30
    if recurring.upper() == "Y":
        rec_freq = input("How often will this bill recur (days)? ")
        while True: 
            try:
                rec_freq = int(rec_freq)
                break
            except ValueError:
                rec_freq = input("Please enter a valid number of days: ")
    while True: 
        try:
            bill_amount = float(bill_amount)
            break
        except ValueError:
            bill_amount = input("Please enter a valid amount: $")
    due_date = input("Please enter the bill's due date (YYYY-MM-DD): ")
    while True: 
        try: 
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            if due_date < date.today():
                due_date = input("Please enter a date in the future: ")
                continue
            break                
        except ValueError:
            due_date = input("Please enter valid date (YYYY-MM-DD): ")
    account.add_bill(bill_name, bill_amount, due_date, recurring, rec_freq)
    save_data(identity_dir, account_dir)


#Call spending instance and ensure all inputs are valid
def create_spending(account):
    cat_name = input("Please enter category name: ")
    cat_amount = input("Please enter category amount: $")
    while True:
        try:
            cat_amount = float(cat_amount)
            break
        except ValueError:
            cat_amount = input("Please enter a valid amount: $")
    account.add_spending(cat_name, cat_amount)
    save_data(identity_dir, account_dir)


#Request Reccomendations
def get_reccomendations(account):
    rec = Reccomendation(account)
    report = rec.generate_report()
    print("\n=== Budget Recommendations ===")
    for line in report:
        print(line)


def main():
    while True:
        account = create_or_login()
        if account == None:
            return
        account.update_balance()
        while True:
            order = input("What would you like to do?\n1: summaraize account\n2: deposit money\n3: add bill \
                        \n4: add spending\n5: get recommendations\n6: log-out\nEnter number command: ").strip()
            if order == "1":
                summarize_account(account)
            elif order == "2":
                deposit_funds(account)
                print("\n")
                save_data(identity_dir, account_dir)
            elif order == "3":
                create_bill(account)
                print("\n")
                save_data(identity_dir, account_dir)
            elif order == "4":
                create_spending(account)
                print("\n")
                save_data(identity_dir, account_dir)
            elif order =="5":
                get_reccomendations(account)
                print("\n")
            elif order == "6":
                print("Logging out...")
                print("\n")
                break

if __name__ == "__main__":
    main()