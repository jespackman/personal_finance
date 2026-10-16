import json
from datetime import date, timedelta
from nicegui import ui
from nicegui.testing import User
from conftest import TEST_DATA_FILE


#Find an input by its label; index picks between fields that share a label, in page order
def field(user, kind, label, index=0):
    found = sorted((e for e in user.find(kind=kind).elements if e.props.get("label") == label), key=lambda e: e.id)
    return found[index]


async def sign_up(user, name="Alice", username="alice", password="password123", confirm=None):
    await user.open("/")
    await user.should_see("Log in")
    field(user, ui.input, "Name").value = name
    field(user, ui.input, "Username", 1).value = username
    field(user, ui.input, "Password", 1).value = password
    field(user, ui.input, "Confirm password").value = password if confirm is None else confirm
    user.find(kind=ui.button, content="Create account").click()


async def log_in(user, username, password):
    field(user, ui.input, "Username", 0).value = username
    field(user, ui.input, "Password", 0).value = password
    user.find(kind=ui.button, content="Log in").click()


async def log_out(user):
    user.find("Log out").click()
    await user.should_see("Log in")


async def test_redirects_to_login_when_logged_out(user: User):
    await user.open("/")
    await user.should_see("Log in")
    await user.should_not_see("Balance")


async def test_wrong_password_is_rejected(user: User):
    await sign_up(user)
    await user.should_see("Account created!")
    await log_out(user)
    await log_in(user, "alice", "wrongpassword")
    await user.should_see("Username or password is incorrect.")


async def test_duplicate_username_is_rejected(user: User):
    await sign_up(user)
    await user.should_see("Account created!")
    await log_out(user)
    await sign_up(user, name="Someone Else", username="ALICE")
    await user.should_see("That username is already taken.")


async def test_two_people_can_share_a_name(user: User):
    await sign_up(user, name="Alex", username="alex1")
    await user.should_see("Account created!")
    await log_out(user)
    await sign_up(user, name="Alex", username="alex2")
    await user.should_see("Account created!")


async def test_signup_validation(user: User):
    await sign_up(user, username="a b")
    await user.should_see("Username can only contain letters, numbers and underscores.")
    await sign_up(user, password="short")
    await user.should_see("Password must be at least 8 characters.")
    await sign_up(user, confirm="different123")
    await user.should_see("Passwords do not match.")


async def test_password_is_not_stored_in_plain_text(user: User):
    await sign_up(user)
    await user.should_see("Account created!")
    assert "password123" not in open(TEST_DATA_FILE).read()


async def test_full_flow(user: User):
    await sign_up(user, name="Nice Tester", username="nicetester", password="secretpass")
    await user.should_see("Account created! Welcome, Nice Tester.")

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
    saved = data["accounts"][data["identities"]["nicetester"]["account_id"]]
    assert saved["name"] == "Nice Tester"
    assert saved["deposits"][0]["amount"] == 300
    assert saved["balance"] == 260
    assert saved["spendings"][0]["category"] == "Groceries"
    assert saved["bills"][0]["name"] == "Rent"

    #Log out and back in (usernames are case-insensitive)
    await log_out(user)
    await log_in(user, "NiceTester", "secretpass")
    await user.should_see("Rent")
    await user.should_see("Groceries")
