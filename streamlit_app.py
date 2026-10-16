#Streamlit interface. Run with: streamlit run streamlit_app.py
from datetime import date
import pandas as pd
import streamlit as st
from Recommendation import Recommendation
from storage import load_data, save_data, login, create_account, signup_error


st.set_page_config(page_title="Finance App", page_icon="💰", layout="wide")

#Streamlit reruns this script on every click, so reload from disk each time to stay in sync
identity_dir, account_dir = load_data()


def save():
    save_data(identity_dir, account_dir)


#Login / create account screen
def login_page():
    st.title("💰 Finance App")
    login_tab, create_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log in"):
                account = login(identity_dir, account_dir, username, password)
                if account is None:
                    st.error("Username or password is incorrect.")
                else:
                    st.session_state.account_id = account.id_num
                    st.rerun()

    with create_tab:
        with st.form("create"):
            name = st.text_input("Name")
            username = st.text_input("Username", help="3 to 20 letters, numbers or underscores")
            password = st.text_input("Password", type="password", help="At least 8 characters")
            confirm = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create account"):
                error = signup_error(identity_dir, name, username, password, confirm)
                if error:
                    st.error(error)
                else:
                    account = create_account(identity_dir, account_dir, name, username, password)
                    st.session_state.account_id = account.id_num
                    st.session_state.new_account = True
                    st.rerun()


def overview_tab(account):
    col1, col2, col3 = st.columns(3)
    col1.metric("Balance", f"${account.balance:,.2f}")
    col2.metric("Average monthly income", f"${account.average_income():,.2f}")
    col3.metric("Last month's income", f"${account.last_month_income():,.2f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Spending this month")
        by_category = account.spending_by_category()
        if by_category:
            df = pd.DataFrame(by_category.items(), columns=["Category", "Amount"]).set_index("Category")
            st.bar_chart(df)
        else:
            st.caption("No spending recorded this month.")
    with right:
        st.subheader("Upcoming bills")
        if account.bills:
            st.dataframe(pd.DataFrame([{"Name": b.name, "Amount": b.amount, "Due": b.due_date,
                                        "Recurring": f"Every {b.frequency} days" if b.recurring else "No"}
                                       for b in sorted(account.bills, key=lambda b: b.due_date)]),
                         hide_index=True, column_config={"Amount": st.column_config.NumberColumn(format="$%.2f")})
        else:
            st.caption("No upcoming bills.")


def deposit_tab(account):
    with st.form("deposit", clear_on_submit=True):
        amount = st.number_input("Amount ($)", min_value=0.01, step=10.0, format="%.2f")
        if st.form_submit_button("Deposit"):
            account.add_amount(amount)
            save()
            st.success(f"Deposited ${amount:,.2f}. Your balance is now ${account.balance:,.2f}.")


def bill_tab(account):
    with st.form("bill", clear_on_submit=True):
        name = st.text_input("Bill name")
        amount = st.number_input("Amount ($)", min_value=0.01, step=10.0, format="%.2f")
        due_date = st.date_input("Due date", min_value=date.today())
        recurring = st.checkbox("Recurring")
        frequency = st.number_input("Recurs every (days)", min_value=1, value=30, step=1)
        if st.form_submit_button("Add bill"):
            if not name.strip():
                st.error("Please enter a bill name.")
            else:
                account.add_bill(name.strip(), amount, due_date, recurring, int(frequency))
                save()
                st.success(f"Added bill '{name.strip()}'.")


def spending_tab(account):
    with st.form("spending", clear_on_submit=True):
        category = st.text_input("Category", help="e.g. Groceries, Gas, Dining Out, Entertainment")
        amount = st.number_input("Amount ($)", min_value=0.01, step=5.0, format="%.2f")
        if st.form_submit_button("Add spending"):
            if not category.strip():
                st.error("Please enter a category.")
            else:
                account.add_spending(category.strip().title(), amount)
                save()
                st.success(f"Added ${amount:,.2f} to {category.strip().title()}.")


def recommendations_tab(account):
    recommendation = Recommendation(account)
    current = recommendation.total_by_type()
    recommended = recommendation.recommended_spent()
    st.caption(f"Based on predicted monthly income of ${account.predicted_income:,.2f}.")
    df = pd.DataFrame({"Spent": [current[t] for t in current],
                       "Recommended": [recommended[t] for t in current]}, index=list(current))
    st.bar_chart(df, stack=False)
    for line in recommendation.generate_report():
        st.write("- " + line)


def account_page(account):
    pages = {"Overview": overview_tab, "Deposit": deposit_tab, "Bills": bill_tab,
             "Spending": spending_tab, "Recommendations": recommendations_tab}
    with st.sidebar:
        st.header(account.name)
        choice = st.radio("Go to", list(pages), label_visibility="collapsed")
        if st.button("Log out"):
            del st.session_state.account_id
            st.rerun()

    if st.session_state.pop("new_account", False):
        st.success(f"Account created! Welcome, {account.name}.")

    st.title(choice)
    pages[choice](account)


account = account_dir.get(st.session_state.get("account_id"))
if account is None:
    login_page()
else:
    account.update_balance()
    save()
    account_page(account)
