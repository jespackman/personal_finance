from datetime import date

class Spending:
    def __init__(self, name, amount, category = "General", spending_date = None):
        self.name = name
        self.amount = float(amount)
        self.category = category
        self.date = spending_date if spending_date else date.today()


    # Class object to dictionary
    def to_dict(self):
        return {"name": self.name, "amount": self.amount, "category": self.category, "date": self.date.isoformat()}


    # Dictionary to Class Object
    @staticmethod
    def from_dict(data):
        return Spending(name =data ["name"], amount = data["amount"], category = data.get("category", "General"),
                        spending_date = date.fromisoformat(data["date"]))
