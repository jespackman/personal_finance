#Import Classes
from datetime import datetime, date
from getpass import getpass
from Recommendation import Recommendation
from storage import load_data, save_data, username_taken, username_error, password_error, login, create_account


#Load data in from json and make usable
identity_dir, account_dir = load_data()


#Input helpers: keep asking until the answer is valid
def ask_float(prompt, minimum = 0.0):
    value = input(prompt)
    while True:
        try:
            amount = float(value)
            if amount < minimum:
                value = input(f"Please enter an amount of at least ${minimum:.2f}: $")
                continue
            return amount
        except ValueError:
            value = input("Please enter a valid amount: $")


def ask_int(prompt, minimum = 1):
    value = input(prompt)
    while True:
        try:
            number = int(value)
            if number < minimum:
                value = input(f"Please enter a number of at least {minimum}: ")
                continue
            return number
        except ValueError:
            value = input("Please enter a valid whole number: ")


def ask_future_date(prompt):
    value = input(prompt)
    while True:
        try:
            due_date = datetime.strptime(value, "%Y-%m-%d").date()
            if due_date < date.today():
                value = input("Please enter a date that is not in the past: ")
                continue
            return due_date
        except ValueError:
            value = input("Please enter valid date (YYYY-MM-DD): ")


#Create Account Function
def create_or_login():
    username = input("Welcome! Please enter your username: ")
    if username_taken(identity_dir, username):
        while True:
            password = getpass("Please enter your password (or press Enter to cancel): ")
            if password == "":
                return None
            account = login(identity_dir, account_dir, username, password)
            if account is not None:
                return account
            print("Password incorrect. Please try again.")
    answer = input("There is no account with that username. Would you like to create one? ")
    if answer.upper().strip() not in ("YES", "Y"):
        print("Returning to login screen...")
        return None
    while username_error(username):
        print(username_error(username))
        username = input("Please choose a username: ")
        if username_taken(identity_dir, username):
            print("That username is already taken.")
            username = ""
    name = input("Please enter your name: ").strip()
    while not name:
        name = input("Please enter your name: ").strip()
    while True:
        password = getpass("Please choose a password: ")
        if password_error(password):
            print(password_error(password))
        elif getpass("Please confirm your password: ") != password:
            print("Passwords do not match.")
        else:
            break
    account = create_account(identity_dir, account_dir, name, username, password)
    print(f"Account created! Welcome, {account.name}.")
    #Money already in the account is the starting balance, not income
    account.set_starting_balance(ask_float("How much money is already in this account? $", minimum = 0))
    save_data(identity_dir, account_dir)
    return account

#Call summarize function and print
def summarize_account(account):
    print(account.summarize())


#Call deposit instance and ensure all inputs are valid
def deposit_funds(account):
    amount = ask_float("Please enter the amount deposited: $", minimum = 0.01)
    account.add_amount(amount)
    print(f"Your account balance is now ${account.balance:.2f}.")


#Call bill instance and ensure all inputs are valid
def create_bill(account):
    bill_name = input("Please enter the bill name: ")
    bill_amount = ask_float("Please enter the bill amount: $", minimum = 0.01)
    recurring = input("Is this bill recurring? (Y/N) ").strip().upper() == "Y"
    rec_freq = 30
    monthly = False
    if recurring:
        monthly = input("Does it recur monthly (M) or every set number of days (D)? ").strip().upper() != "D"
        if not monthly:
            rec_freq = ask_int("How often will this bill recur (days)? ")
    due_date = ask_future_date("Please enter the bill's due date (YYYY-MM-DD): ")
    account.add_bill(bill_name, bill_amount, due_date, recurring, rec_freq, monthly)


#Call spending instance and ensure all inputs are valid
def create_spending(account):
    cat_name = input("Please enter category name: ").strip().title()
    cat_amount = ask_float("Please enter category amount: $", minimum = 0.01)
    account.add_spending(cat_name, cat_amount)


#Request Recommendations
def get_recommendations(account):
    report = Recommendation(account).generate_report()
    print("\n=== Budget Recommendations ===")
    for line in report:
        print(line)


MENU = """What would you like to do?
1: summarize account
2: deposit money
3: add bill
4: add spending
5: get recommendations
6: log-out
Enter number command: """

#Commands that change the account and need saving afterwards
ACTIONS = {"2": deposit_funds, "3": create_bill, "4": create_spending}


def main():
    while True:
        account = create_or_login()
        if account is None:
            return
        account.update_balance()
        save_data(identity_dir, account_dir)
        while True:
            order = input(MENU).strip()
            if order == "1":
                summarize_account(account)
            elif order in ACTIONS:
                ACTIONS[order](account)
                save_data(identity_dir, account_dir)
                print()
            elif order == "5":
                get_recommendations(account)
                print()
            elif order == "6":
                print("Logging out...\n")
                break
            else:
                print("Please enter a number from 1 to 6.\n")

if __name__ == "__main__":
    main()
