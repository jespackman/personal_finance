from datetime import date
from Bill import Bill
from Spending import Spending


class Account:

    #Initiate a class taking name as a string, predicted income per month as an integer, 
    # bills as a list of tuples (now a list of Bill class), estimated spending as a dictionary, starting balance
    def __init__(self, name, id_num, bills = None, spending = None, balance = 0, deposits = None):
        self.name = name
        self.id_num = id_num
        self.bills = bills if bills is not None else []
        self.spending = spending if spending is not None else {}
        self.balance = float(balance)
        self.deposits = deposits if deposits is not None else []
        self.spendings = []
        self.predicted_income = self.last_month_income()
    

    #Manually added money to balance
    def add_amount(self, amount=0.0, add_date = None):
        if add_date == None:
            add_date = date.today()
        self.balance += amount
        self.deposits.append((amount, add_date))
        return self.balance
        

    #Add expense
    def add_spending(self, category, amount: float, spending_date = date.today()):
        spending_entry = Spending(category, amount, category, spending_date)
        self.spendings.append(spending_entry)
        self.spending[category] = self.spending.get(category, 0) + amount


    #Add bills as spending
    def add_bill_to_spendings(self, bill):
            bill_as_spending = Spending(bill.name, bill.amount, "Bills", bill.due_date)
            self.spendings.append(bill_as_spending)


    #Add bill, due date must be "YYYY-MM-DD"
    def add_bill(self, bill_name, amount: float, due_date: date, recurring = False, frequency = 30):
        bill = (Bill(bill_name, amount, due_date, recurring, frequency))
        self.bills.append(bill)
        self.add_bill_to_spendings(bill)


    #Suggest spending habits and money allocation
    def suggest_spending(self):
        pass


    #Update balance when bills go through and add income
    def update_balance(self, today = None):
        if today == None:
            today = date.today()
        bills_due = 0
        new_bills = []
        for bill in self.bills:
            if bill.is_due(today):
                bills_due += bill.amount
                bill.mark_paid()
                if bill.recurring:
                    next_bill = bill.next_due()
                    new_bills.append(next_bill)
                    self.add_bill_to_spendings(next_bill)
            else:
                new_bills.append(bill)
        self.balance -= bills_due
        self.bills = new_bills


    #Find average amount added to the account per month
    def average_income(self):
        if not self.deposits:
            return 0
        dates = []
        total_income = 0
        for amount, add_date in self.deposits:
            dates.append(add_date)
            total_income += amount
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
        avg_income = self.average_income()
        summary += f"Average Monthly Income: ${avg_income:.2f}\n"
        lst_mnth_income = self.last_month_income()
        summary += f"Last Month's Income: ${lst_mnth_income:.2f}\n"
        summary += f"Spending:\n"
        for category, amount in self.spending.items():
            summary += f" - {category}: ${amount:.2f}/month\n"
        summary += f"Bills:\n"
        for bill in self.bills:
            summary += f" - {bill}\n"
        return summary


    #Store accounts as dictionaries
    def acc_to_dict(self):
            bills_list = []
            for bill in self.bills:
                bill_dict = {"name": bill.name, "amount": bill.amount, "due_date": bill.due_date.isoformat(), "paid": bill.paid, "recurring": bill.recurring, "frequency": bill.frequency}
                bills_list.append(bill_dict)
            return {"name": self.name, "id_num": self.id_num, "balance": self.balance, "bills": bills_list, "spending": self.spending}


#Make accounts from dictionary, must be static method because starting from scratch
    @staticmethod
    def dict_to_acc(data):
        bills_list = []
        for bill in data.get("bills", []):
            bll = Bill(bill["name"], bill["amount"], date.fromisoformat(bill["due_date"]), bill.get("paid", False),
                        bill.get("recurring", False), bill.get("frequency", 30))
            bills_list.append(bll)
        return Account(data["name"], data["id_num"], balance = data["balance"], bills = bills_list, 
                       spending = data["spending"])
        