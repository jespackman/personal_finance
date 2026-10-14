#Import Classes
import json
import os
import random
from Account import Account


#Retrieve data from json file stored next to this script, regardless of the working directory
#(FINANCE_APP_DATA_FILE can point somewhere else, e.g. for testing)
DATA_FILE = os.environ.get("FINANCE_APP_DATA_FILE",
                           os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json"))


#Load identities (name -> account number) and accounts (account number -> Account)
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {"identities": {}, "accounts": {}}
    accounts = {}
    for acc_id, acc_data in data["accounts"].items():
        accounts[acc_id] = Account.dict_to_acc(acc_data)
    return data["identities"], accounts


#Save accounts as dictionaries
def save_data(identities, accounts):
    accounts_dict = {}
    for acc_id, acc in accounts.items():
        accounts_dict[acc_id] = acc.acc_to_dict()
    data = {"identities": identities, "accounts": accounts_dict}
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)


#Names are stored upper case so logins are case-insensitive
def normalize_name(name):
    return name.strip().upper()


def account_exists(identities, name):
    return normalize_name(name) in identities


#Return the account if the name and account number match, otherwise None
def login(identities, accounts, name, id_num):
    name = normalize_name(name)
    if identities.get(name) == id_num.strip():
        return accounts[identities[name]]
    return None


#Create an account with a unique random account number and save it
def create_account(identities, accounts, name):
    name = normalize_name(name)
    while True:
        id_num = str(random.randint(100_000_000, 999_999_999))
        if id_num not in identities.values():
            break
    identities[name] = id_num
    account = Account(name, id_num)
    accounts[id_num] = account
    save_data(identities, accounts)
    return account
