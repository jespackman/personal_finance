#Import Classes
import hashlib
import hmac
import json
import os
import random
import secrets
from Account import Account


#Retrieve data from json file stored next to this script, regardless of the working directory
#(FINANCE_APP_DATA_FILE can point somewhere else, e.g. for testing)
DATA_FILE = os.environ.get("FINANCE_APP_DATA_FILE",
                           os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json"))


#Load identities (username -> account id and password hash) and accounts (account id -> Account)
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


#Usernames are stored lower case so logins are case-insensitive
def normalize_username(username):
    return username.strip().lower()


def username_taken(identities, username):
    return normalize_username(username) in identities


#Return an error message for an invalid username, or None if it is fine
def username_error(username):
    username = normalize_username(username)
    if not 3 <= len(username) <= 20:
        return "Username must be 3 to 20 characters."
    if not all(char.isalnum() or char == "_" for char in username):
        return "Username can only contain letters, numbers and underscores."
    return None


#Return an error message for a weak password, or None if it is fine
def password_error(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    return None


#Check a whole sign-up form at once; returns the first problem found, or None
def signup_error(identities, name, username, password, confirm):
    if not name.strip():
        return "Please enter your name."
    if username_error(username):
        return username_error(username)
    if username_taken(identities, username):
        return "That username is already taken."
    if password_error(password):
        return password_error(password)
    if password != confirm:
        return "Passwords do not match."
    return None


#Passwords are never stored, only a salted PBKDF2 hash of them
HASH_ITERATIONS = 600_000

def hash_password(password, salt = None):
    salt = salt if salt is not None else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, HASH_ITERATIONS)
    return salt.hex() + "$" + digest.hex()


def check_password(password, stored_hash):
    salt_hex, digest_hex = stored_hash.split("$")
    return hmac.compare_digest(hash_password(password, bytes.fromhex(salt_hex)), stored_hash)


#Return the account if the username and password match, otherwise None
def login(identities, accounts, username, password):
    identity = identities.get(normalize_username(username))
    if identity is None or not check_password(password, identity["password_hash"]):
        return None
    return accounts[identity["account_id"]]


#Create an account with a unique internal id, store the username and password hash, and save it.
#Check username_taken, username_error and password_error first.
def create_account(identities, accounts, name, username, password):
    while True:
        id_num = str(random.randint(100_000_000, 999_999_999))
        if id_num not in accounts:
            break
    identities[normalize_username(username)] = {"account_id": id_num, "password_hash": hash_password(password)}
    account = Account(name.strip(), id_num)
    accounts[id_num] = account
    save_data(identities, accounts)
    return account
