import json
from datetime import date, timedelta
from nicegui import ui
from nicegui.testing import User
from conftest import TEST_DATA_FILE


#Find an input by its label; index picks between fields that share a label, in page order
def field(user, kind, label, index=0):
    found = sorted((e for e in user.find(kind=kind).elements if e.props.get("label") == label), key=lambda e: e.id)
    return found[index]


async def create_account(user, name):
    await user.open("/")
    await user.should_see("Log in")
    field(user, ui.input, "Name", 1).value = name
    user.find(kind=ui.button, content="Create account").click()
    await user.should_see("Account created!")


async def test_redirects_to_login_when_logged_out(user: User):
    await user.open("/")
    await user.should_see("Log in")
    await user.should_not_see("Balance")


async def test_wrong_account_number_is_rejected(user: User):
    await create_account(user, "alice")
    user.find("Log out").click()
    await user.should_see("Log in")
    field(user, ui.input, "Name", 0).value = "alice"
    field(user, ui.input, "Account number").value = "123"
    user.find(kind=ui.button, content="Log in").click()
    await user.should_see("Name or account number is incorrect.")


async def test_duplicate_name_is_rejected(user: User):
    await create_account(user, "alice")
    user.find("Log out").click()
    await user.should_see("Log in")
    field(user, ui.input, "Name", 1).value = "ALICE"
    user.find(kind=ui.button, content="Create account").click()
    await user.should_see("An account with that name already exists.")


async def test_full_flow(user: User):
    await create_account(user, "nicetester")

    field(user, ui.number, "Amount", 0).value = 300
    user.find(kind=ui.button, content="Deposit").click()
    await user.should_see("Your balance is now $300.00")

    field(user, ui.input, "Category").value = "groceries"
    field(user, ui.number, "Amount", 2).value = 40
    user.find(kind=ui.button, content="Add spending").click()
    await user.should_see("Added $40.00 to Groceries")

    field(user, ui.input, "Bill name").value = "Rent"
    field(user, ui.number, "Amount", 1).value = 800
    user.find(kind=ui.date).elements.pop().value = (date.today() + timedelta(days=5)).isoformat()
    user.find(kind=ui.button, content="Add bill").click()
    await user.should_see("Added bill 'Rent'")
    await user.should_see("You are under your necessities budget")

    #Empty deposit is rejected
    user.find(kind=ui.button, content="Deposit").click()
    await user.should_see("Please enter an amount")

    #Everything was saved to disk
    data = json.load(open(TEST_DATA_FILE))
    saved = data["accounts"][data["identities"]["NICETESTER"]]
    assert saved["deposits"][0]["amount"] == 300
    assert saved["balance"] == 260
    assert saved["spendings"][0]["category"] == "Groceries"
    assert saved["bills"][0]["name"] == "Rent"

    #Log out and back in with the account number
    user.find("Log out").click()
    await user.should_see("Log in")
    field(user, ui.input, "Name", 0).value = "NiceTester"
    field(user, ui.input, "Account number").value = data["identities"]["NICETESTER"]
    user.find(kind=ui.button, content="Log in").click()
    await user.should_see("Rent")
    await user.should_see("Groceries")
