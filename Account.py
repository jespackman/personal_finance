from datetime import date
from Bill import Bill
from Spending import Spending


class Account:

    #Initiate a class taking name as a string, account number, bills as a list of Bill,
    # spendings as a list of Spending, current balance, deposits as a list of (amount, date),
    # and the balance the account was opened with
    def __init__(self, name, id_num, bills = None, spendings = None, balance = 0, deposits = None, starting_balance = 0):
        self.name = name
        self.id_num = id_num
        self.bills = bills if bills is not None else []
        self.spendings = spendings if spendings is not None else []
        self.balance = float(balance)
        self.deposits = deposits if deposits is not None else []
        self.starting_balance = float(starting_balance)


    #Expected monthly income: last month's deposits, falling back to the overall monthly average
    @property
    def predicted_income(self):
        return self.last_month_income() or self.average_income()


    #Money already in the account when it was opened; not a deposit, so it does not count as income
    def set_starting_balance(self, amount):
        self.balance += amount - self.starting_balance
        self.starting_balance = amount
        return self.balance


    #Manually added money to balance
    def add_amount(self, amount=0.0, add_date = None):
        if add_date is None:
            add_date = date.today()
        self.balance += amount
        self.deposits.append((amount, add_date))
        return self.balance


    #Add expense and take it out of the balance
    def add_spending(self, category, amount: float, spending_date = None):
        self.balance -= amount
        self.spendings.append(Spending(category, amount, category, spending_date))


    #Add bill; it is recorded as spending once it is actually charged in update_balance
    def add_bill(self, bill_name, amount: float, due_date: date, recurring = False, frequency = 30, monthly = False):
        self.bills.append(Bill(bill_name, amount, due_date, recurring=recurring, frequency=frequency, monthly=monthly))


    #Charge every bill that has come due, including missed cycles of recurring bills
    def update_balance(self, today = None):
        if today is None:
            today = date.today()
        remaining = []
        for bill in self.bills:
            while bill is not None and bill.is_due(today):
                self.balance -= bill.amount
                bill.mark_paid()
                self.spendings.append(Spending(bill.name, bill.amount, "Bills", bill.due_date))
                bill = bill.next_due()
            if bill is not None:
                remaining.append(bill)
        self.bills = remaining


    #Spendings that fall in the given month (defaults to the current month)
    def monthly_spendings(self, year = None, month = None):
        today = date.today()
        year = year or today.year
        month = month or today.month
        return [s for s in self.spendings if s.date.year == year and s.date.month == month]


    #Total spent per category in the given month
    def spending_by_category(self, year = None, month = None):
        totals = {}
        for spending in self.monthly_spendings(year, month):
            totals[spending.category] = totals.get(spending.category, 0) + spending.amount
        return totals


    #Find average amount added to the account per month
    def average_income(self):
        if not self.deposits:
            return 0
        dates = [add_date for _, add_date in self.deposits]
        total_income = sum(amount for amount, _ in self.deposits)
        first_date = min(dates)
        recent_date = max(dates)
        months = (recent_date.year - first_date.year)*12 + (recent_date.month - first_date.month) + 1
        return round(total_income/months, 2)


    #Find the ammount added to the account in the last month
    def last_month_income(self):
        if not self.deposits:
            return 0
        today = date.today()
        if today.month == 1:
            last_month = 12
            last_year = today.year - 1
        else:
            last_month = today.month - 1
            last_year = today.year
        monthly_amount = 0
        for amount, add_date in self.deposits:
            if add_date.year == last_year and add_date.month == last_month:
                monthly_amount += amount
        return round(monthly_amount, 2)


    #Summarize account
    def summarize(self):
        summary = f"Account: {self.name}\n"
        summary += f"Balance: ${self.balance:.2f}\n"
        summary += f"Average Monthly Income: ${self.average_income():.2f}\n"
        summary += f"Last Month's Income: ${self.last_month_income():.2f}\n"
        summary += "Spending This Month:\n"
        for category, amount in self.spending_by_category().items():
            summary += f" - {category}: ${amount:.2f}\n"
        summary += "Upcoming Bills:\n"
        for bill in self.bills:
            summary += f" - {bill}\n"
        return summary


    #Store accounts as dictionaries
    def acc_to_dict(self):
        return {"name": self.name, "id_num": self.id_num, "balance": self.balance,
                "starting_balance": self.starting_balance,
                "bills": [bill.to_dict() for bill in self.bills],
                "spendings": [spending.to_dict() for spending in self.spendings],
                "deposits": [{"amount": amount, "date": add_date.isoformat()} for amount, add_date in self.deposits]}


    #Make accounts from dictionary, must be static method because starting from scratch
    @staticmethod
    def dict_to_acc(data):
        bills = [Bill.from_dict(bill) for bill in data.get("bills", [])]
        spendings = [Spending.from_dict(spending) for spending in data.get("spendings", [])]
        deposits = [(dep["amount"], date.fromisoformat(dep["date"])) for dep in data.get("deposits", [])]
        return Account(data["name"], data["id_num"], balance = data.get("balance", 0), bills = bills,
                       spendings = spendings, deposits = deposits, starting_balance = data.get("starting_balance", 0))
