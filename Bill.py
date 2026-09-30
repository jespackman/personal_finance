from datetime import timedelta

class Bill:
    def __init__(self, name, amount, due_date, paid = False, recurring = False, frequency = 30):
        #Take name of bill, amount due date, payment status and reccurrence (Boolean and frequency in days)
        self.name = name
        self.amount = amount
        self.due_date = due_date
        self.paid = paid
        self.recurring = recurring
        self.frequency = frequency


    def mark_paid(self):
        self.paid = True


    def is_due(self, today):
        if today > self.due_date and not self.paid:
            return True
        else:
            return False
        

    def next_due(self):
        if not self.recurring:
            return
        new_due_date = self.due_date + timedelta(days=self.frequency)
        return Bill(self.name, self.amount, new_due_date, self.paid, True, self.frequency)


    def __str__(self):
        if self.paid:
            status = "Paid"
        else: 
            status = "Unpaid"
        if self.recurring:
            recur = f" (Recurring every {self.frequency} days)"
        else:
            recur = ""
        return f"{self.name}: ${self.amount} due {self.due_date} ({status}{recur})"

