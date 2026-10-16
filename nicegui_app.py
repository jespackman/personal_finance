#NiceGUI interface. Run with: python nicegui_app.py  (then open http://localhost:8080)
import os
import secrets
from datetime import date
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from Recommendation import Recommendation
from storage import load_data, save_data, login, create_account, signup_error


#The server stays running, so load once and keep the data in memory
identity_dir, account_dir = load_data()


def save():
    save_data(identity_dir, account_dir)


#The logged-in account's id is kept in the browser's session storage
def current_account():
    return account_dir.get(app.storage.user.get("account_id"))


def money(amount):
    return f"${amount:,.2f}"


@ui.page("/login")
def login_page():
    #Redirect with an HTTP response (not ui.navigate) so the session cookie is kept
    if current_account() is not None:
        return RedirectResponse("/")

    def do_login():
        account = login(identity_dir, account_dir, login_username.value or "", login_password.value or "")
        if account is None:
            ui.notify("Username or password is incorrect.", type="negative")
            return
        app.storage.user["account_id"] = account.id_num
        ui.navigate.to("/")

    def do_create():
        name, username = new_name.value or "", new_username.value or ""
        password, confirm = new_password.value or "", new_confirm.value or ""
        error = signup_error(identity_dir, name, username, password, confirm)
        if error:
            ui.notify(error, type="negative")
            return
        account = create_account(identity_dir, account_dir, name, username, password)
        app.storage.user["account_id"] = account.id_num
        app.storage.user["new_account"] = True
        ui.navigate.to("/")

    with ui.column().classes("absolute-center items-center gap-4"):
        ui.label("💰 Finance App").classes("text-3xl font-bold")
        with ui.card().classes("w-96"):
            with ui.tabs().classes("w-full") as tabs:
                login_tab = ui.tab("Log in")
                create_tab = ui.tab("Create account")
            with ui.tab_panels(tabs, value=login_tab).classes("w-full"):
                with ui.tab_panel(login_tab).classes("gap-2"):
                    login_username = ui.input("Username").classes("w-full")
                    login_password = ui.input("Password", password=True, password_toggle_button=True
                                              ).classes("w-full").on("keydown.enter", do_login)
                    ui.button("Log in", on_click=do_login).classes("w-full")
                with ui.tab_panel(create_tab).classes("gap-2"):
                    new_name = ui.input("Name").classes("w-full")
                    new_username = ui.input("Username").props('hint="3 to 20 letters, numbers or underscores"'
                                                              ).classes("w-full")
                    new_password = ui.input("Password", password=True, password_toggle_button=True
                                            ).props('hint="At least 8 characters"').classes("w-full")
                    new_confirm = ui.input("Confirm password", password=True
                                           ).classes("w-full").on("keydown.enter", do_create)
                    ui.button("Create account", on_click=do_create).classes("w-full")


@ui.page("/")
def main_page():
    account = current_account()
    if account is None:
        return RedirectResponse("/login")
    account.update_balance()
    save()

    def logout():
        app.storage.user.pop("account_id", None)
        ui.navigate.to("/login")

    with ui.header().classes("items-center justify-between"):
        ui.label(f"💰 {account.name}").classes("text-xl font-bold")
        ui.button("Log out", on_click=logout).props("flat color=white")

    if app.storage.user.pop("new_account", False):
        with ui.card().classes("w-full bg-green-1"):
            ui.label(f"Account created! Welcome, {account.name}.")

    #Sections that show account data are refreshable so they update after every change
    @ui.refreshable
    def overview():
        with ui.row().classes("w-full gap-4"):
            for title, value in [("Balance", account.balance),
                                 ("Average monthly income", account.average_income()),
                                 ("Last month's income", account.last_month_income())]:
                with ui.card().classes("flex-1"):
                    ui.label(title).classes("text-sm opacity-70")
                    ui.label(money(value)).classes("text-2xl font-bold")

        with ui.row().classes("w-full gap-4 items-stretch"):
            with ui.card().classes("flex-1 min-w-80"):
                ui.label("Spending this month").classes("text-lg font-bold")
                by_category = account.spending_by_category()
                if by_category:
                    ui.echart({"tooltip": {"trigger": "item", "valueFormatter": "(v) => '$' + v.toFixed(2)"},
                               "series": [{"type": "pie", "radius": ["40%", "70%"],
                                           "data": [{"name": c, "value": round(a, 2)} for c, a in by_category.items()]}]}
                              ).classes("h-72")
                else:
                    ui.label("No spending recorded this month.").classes("opacity-70")

            with ui.card().classes("flex-1 min-w-80"):
                ui.label("Upcoming bills").classes("text-lg font-bold")
                if account.bills:
                    ui.table(columns=[{"name": "name", "label": "Name", "field": "name", "align": "left"},
                                      {"name": "amount", "label": "Amount", "field": "amount"},
                                      {"name": "due", "label": "Due", "field": "due", "sortable": True},
                                      {"name": "recurring", "label": "Recurring", "field": "recurring"}],
                             rows=[{"name": b.name, "amount": money(b.amount), "due": b.due_date.isoformat(),
                                    "recurring": f"Every {b.frequency} days" if b.recurring else "No"}
                                   for b in sorted(account.bills, key=lambda b: b.due_date)]
                             ).classes("w-full").props("flat")
                else:
                    ui.label("No upcoming bills.").classes("opacity-70")

    @ui.refreshable
    def recommendations():
        recommendation = Recommendation(account)
        current = recommendation.total_by_type()
        recommended = recommendation.recommended_spent()
        ui.label(f"Based on predicted monthly income of {money(account.predicted_income)}.").classes("opacity-70")
        ui.echart({"tooltip": {"trigger": "axis", "valueFormatter": "(v) => '$' + v.toFixed(2)"},
                   "legend": {},
                   "xAxis": {"type": "category", "data": list(current)},
                   "yAxis": {"type": "value"},
                   "series": [{"name": "Spent", "type": "bar", "data": [round(current[t], 2) for t in current]},
                              {"name": "Recommended", "type": "bar",
                               "data": [round(recommended[t], 2) for t in current]}]}).classes("w-full h-72")
        with ui.column().classes("gap-1"):
            for line in recommendation.generate_report():
                ui.label("• " + line)

    #Every deposit and spending, newest first
    @ui.refreshable
    def history():
        rows = [{"date": d.isoformat(), "type": "Deposit", "description": "Deposit", "amount": money(a)}
                for a, d in account.deposits]
        rows += [{"date": s.date.isoformat(), "type": "Spending", "description": s.category, "amount": money(-s.amount)}
                 for s in account.spendings]
        rows.sort(key=lambda row: row["date"], reverse=True)
        if not rows:
            ui.label("No transactions yet.").classes("opacity-70")
            return
        ui.table(columns=[{"name": "date", "label": "Date", "field": "date", "align": "left", "sortable": True},
                          {"name": "type", "label": "Type", "field": "type", "align": "left"},
                          {"name": "description", "label": "Description", "field": "description", "align": "left"},
                          {"name": "amount", "label": "Amount", "field": "amount"}],
                 rows=rows, pagination=15).classes("w-full").props("flat")

    def changed(message):
        save()
        overview.refresh()
        recommendations.refresh()
        history.refresh()
        ui.notify(message, type="positive")

    def deposit():
        if not deposit_amount.value or deposit_amount.value < 0.01:
            ui.notify("Please enter an amount of at least $0.01.", type="warning")
            return
        account.add_amount(float(deposit_amount.value))
        deposit_amount.value = None
        changed(f"Deposited. Your balance is now {money(account.balance)}.")

    def add_bill():
        name = (bill_name.value or "").strip()
        if not name or not bill_amount.value or bill_amount.value < 0.01:
            ui.notify("Please enter a bill name and an amount of at least $0.01.", type="warning")
            return
        due = date.fromisoformat(bill_due.value)
        if due < date.today():
            ui.notify("The due date cannot be in the past.", type="warning")
            return
        account.add_bill(name, float(bill_amount.value), due, bill_recurring.value, int(bill_frequency.value or 30))
        bill_name.value = ""
        bill_amount.value = None
        changed(f"Added bill '{name}'.")

    def add_spending():
        category = (spending_category.value or "").strip().title()
        if not category or not spending_amount.value or spending_amount.value < 0.01:
            ui.notify("Please enter a category and an amount of at least $0.01.", type="warning")
            return
        account.add_spending(category, float(spending_amount.value))
        spending_amount.value = None
        changed(f"Added {money(account.spendings[-1].amount)} to {category}.")

    with ui.tabs().classes("w-full") as tabs:
        overview_tab = ui.tab("Overview", icon="dashboard")
        deposit_tab = ui.tab("Deposit", icon="savings")
        bills_tab = ui.tab("Bills", icon="receipt_long")
        spending_tab = ui.tab("Spending", icon="shopping_cart")
        recommend_tab = ui.tab("Recommendations", icon="insights")
        history_tab = ui.tab("History", icon="history")

    with ui.tab_panels(tabs, value=overview_tab).classes("w-full max-w-5xl mx-auto"):
        with ui.tab_panel(overview_tab):
            overview()

        with ui.tab_panel(deposit_tab):
            with ui.card().classes("w-96"):
                deposit_amount = ui.number("Amount", prefix="$", min=0.01, step=10, format="%.2f").classes("w-full")
                ui.button("Deposit", on_click=deposit)

        with ui.tab_panel(bills_tab):
            with ui.card().classes("w-96"):
                bill_name = ui.input("Bill name").classes("w-full")
                bill_amount = ui.number("Amount", prefix="$", min=0.01, step=10, format="%.2f").classes("w-full")
                ui.label("Due date").classes("text-sm opacity-70")
                today = date.today()
                bill_due = ui.date(value=today.isoformat()).props(
                    f''':options="d => d >= '{today.strftime('%Y/%m/%d')}'"''')
                bill_recurring = ui.checkbox("Recurring")
                bill_frequency = ui.number("Recurs every (days)", value=30, min=1, step=1, format="%d"
                                           ).classes("w-full").bind_visibility_from(bill_recurring, "value")
                ui.button("Add bill", on_click=add_bill)

        with ui.tab_panel(spending_tab):
            with ui.card().classes("w-96"):
                spending_category = ui.input("Category", autocomplete=["Groceries", "Food", "Gas", "Housing",
                                             "Utilities", "Entertainment", "Shopping", "Dining Out", "Travel",
                                             "Tithing"]).classes("w-full")
                spending_amount = ui.number("Amount", prefix="$", min=0.01, step=5, format="%.2f").classes("w-full")
                ui.button("Add spending", on_click=add_spending)

        with ui.tab_panel(recommend_tab):
            recommendations()

        with ui.tab_panel(history_tab):
            history()


#Secret that signs the login cookie: FINANCE_APP_SECRET if set, otherwise generated once and kept in a local file
def storage_secret():
    if os.environ.get("FINANCE_APP_SECRET"):
        return os.environ["FINANCE_APP_SECRET"]
    secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".nicegui_secret")
    if not os.path.exists(secret_file):
        with open(secret_file, "w") as file:
            file.write(secrets.token_hex(32))
    with open(secret_file, "r") as file:
        return file.read().strip()


if __name__ in {"__main__", "__mp_main__"}:
    #Only reachable from this computer; set FINANCE_APP_HOST=0.0.0.0 to allow other devices on your network.
    #Set FINANCE_APP_NO_BROWSER=1 to stop a browser tab opening on start
    ui.run(title="Finance App", favicon="💰", storage_secret=storage_secret(),
           host=os.environ.get("FINANCE_APP_HOST", "127.0.0.1"),
           show=not os.environ.get("FINANCE_APP_NO_BROWSER"))
