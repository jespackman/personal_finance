#Constant dictionary to divide spending into necessities and wants
CATEGORY_TYPE = {"Food": "Necessity","Groceries": "Necessity","Gas": "Necessity","Housing": "Necessity",
    "Utilities": "Necessity","Bills":"Necessity", "Entertainment": "Want","Shopping": "Want","Dining Out": "Want","Travel": "Want",
    "Tithing":"Tithing"}

#Constant dictionary to decide what percentage of money should go where
BUDGET_RULE = {"Necessity": 0.50, "Want": 0.20, "Saving": 0.20, "Tithing": 0.10}

#Readable names for each spending type
TYPE_LABEL = {"Necessity": "necessities", "Want": "wants", "Tithing": "tithing"}


class Recommendation:
    """
    Compares this month's spending against a budget rule applied to the
    account's predicted monthly income, and reports how to better allocate funds.
    """
    def __init__(self, account):
        self.account = account


    def spending_type(self, spending):
        return CATEGORY_TYPE.get(spending.category.strip().title(), "Want")


    def total_by_type(self):
        totals = {"Necessity": 0, "Want": 0, "Tithing": 0}
        for spending in self.account.monthly_spendings():
            totals[self.spending_type(spending)] += spending.amount
        return totals


    def recommended_spent(self):
        monthly_income = self.account.predicted_income
        return {type_: monthly_income * share for type_, share in BUDGET_RULE.items()}


    def generate_report(self):
        current = self.total_by_type()
        recommended = self.recommended_spent()
        monthly_income = self.account.predicted_income
        report = []
        for type_, label in TYPE_LABEL.items():
            difference = recommended[type_] - current[type_]
            if difference < 0:
                report.append(f"You overspent on {label} by ${-difference:.2f}.")
            else:
                report.append(f"You are under your {label} budget by ${difference:.2f}.")
        saving = round(monthly_income - sum(current.values()), 2)
        target = round(recommended["Saving"], 2)
        report.append(f"It is recommended that you save ${target:.2f} per month.")
        report.append(f"So far this month, you are on track to save ${saving:.2f}.")
        if saving < target:
            report.append(f"You are currently saving ${target - saving:.2f} less than recommended.")
        elif saving == target:
            report.append("You are meeting savings recommendations.")
        else:
            report.append(f"You are currently saving ${saving - target:.2f} more than recommended.")
        return report
