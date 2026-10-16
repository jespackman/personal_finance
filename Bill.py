import calendar
from datetime import date, timedelta

class Bill:
    def __init__(self, name, amount, due_date, paid = False, recurring = False, frequency = 30, monthly = False,
                 day_of_month = None):
        #Take name of bill, amount due date, payment status and reccurrence (Boolean and frequency in days).
        #A monthly bill recurs on the same day each month instead of every frequency days;
        #day_of_month remembers that day so a bill due on the 31st returns to the 31st after a short month
        self.name = name
        self.amount = float(amount)
        self.due_date = due_date
        self.paid = paid
        self.recurring = recurring
        self.frequency = frequency
        self.monthly = monthly
        self.day_of_month = day_of_month if day_of_month is not None else due_date.day


    def mark_paid(self):
        self.paid = True


    def is_due(self, today):
        return today > self.due_date and not self.paid


    #Same day next month, or the last day of next month if it is shorter
    def next_month_date(self):
        year = self.due_date.year + self.due_date.month // 12
        month = self.due_date.month % 12 + 1
        day = min(self.day_of_month, calendar.monthrange(year, month)[1])
        return date(year, month, day)


    #Next occurrence of a recurring bill always starts unpaid
    def next_due(self):
        if not self.recurring:
            return None
        if self.monthly:
            new_due_date = self.next_month_date()
        else:
            new_due_date = self.due_date + timedelta(days=self.frequency)
        return Bill(self.name, self.amount, new_due_date, paid=False, recurring=True, frequency=self.frequency,
                    monthly=self.monthly, day_of_month=self.day_of_month)


    #How often the bill repeats, for display
    def recurrence(self):
        if not self.recurring:
            return "No"
        if self.monthly:
            return "Monthly"
        return f"Every {self.frequency} days"


    # Class object to dictionary
    def to_dict(self):
        return {"name": self.name, "amount": self.amount, "due_date": self.due_date.isoformat(), "paid": self.paid,
                "recurring": self.recurring, "frequency": self.frequency, "monthly": self.monthly,
                "day_of_month": self.day_of_month}


    # Dictionary to Class Object
    @staticmethod
    def from_dict(data):
        return Bill(data["name"], data["amount"], date.fromisoformat(data["due_date"]), paid=data.get("paid", False),
                    recurring=data.get("recurring", False), frequency=data.get("frequency", 30),
                    monthly=data.get("monthly", False), day_of_month=data.get("day_of_month"))


    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        recur = f" (Recurring {self.recurrence().lower()})" if self.recurring else ""
        return f"{self.name}: ${self.amount:.2f} due {self.due_date} ({status}{recur})"
