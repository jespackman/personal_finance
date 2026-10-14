from datetime import date, timedelta

class Bill:
    def __init__(self, name, amount, due_date, paid = False, recurring = False, frequency = 30):
        #Take name of bill, amount due date, payment status and reccurrence (Boolean and frequency in days)
        self.name = name
        self.amount = float(amount)
        self.due_date = due_date
        self.paid = paid
        self.recurring = recurring
        self.frequency = frequency


    def mark_paid(self):
        self.paid = True


    def is_due(self, today):
        return today > self.due_date and not self.paid


    #Next occurrence of a recurring bill always starts unpaid
    def next_due(self):
        if not self.recurring:
            return None
        new_due_date = self.due_date + timedelta(days=self.frequency)
        return Bill(self.name, self.amount, new_due_date, paid=False, recurring=True, frequency=self.frequency)


    # Class object to dictionary
    def to_dict(self):
        return {"name": self.name, "amount": self.amount, "due_date": self.due_date.isoformat(), "paid": self.paid,
                "recurring": self.recurring, "frequency": self.frequency}


    # Dictionary to Class Object
    @staticmethod
    def from_dict(data):
        return Bill(data["name"], data["amount"], date.fromisoformat(data["due_date"]), paid=data.get("paid", False),
                    recurring=data.get("recurring", False), frequency=data.get("frequency", 30))


    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        recur = f" (Recurring every {self.frequency} days)" if self.recurring else ""
        return f"{self.name}: ${self.amount:.2f} due {self.due_date} ({status}{recur})"
