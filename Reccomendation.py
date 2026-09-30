#Constant dictionary to divide spending into necessities and wants
CATEGORY_TYPE = {"Food": "Necessity","Groceries": "Necessity","Gas": "Necessity","Housing": "Necessity",
    "Utilities": "Necessity","Bills":"Necessity", "Entertainment": "Want","Shopping": "Want","Dining Out": "Want","Travel": "Want", 
    "Tithing":"Tithing"}

#Constant dictionary to decide what percentage of money should go where
BUDGET_RULE = {"Necessity": 0.50, "Want": 0.20, "Saving": 0.20, "Tithing": 0.10}


class Reccomendation:
    """
    This class will use information found online about how expensive things are 
    and take into consideration spending habits and bills. It will then give 
    reccomendations on how to better allocate funds. 

    """
    def __init__(self, account):
        self.account = account


    def spending_type(self, spending):
        if spending.category in CATEGORY_TYPE:
            return CATEGORY_TYPE[spending.category]
        return "Want"


    def total_by_type(self):
        totals = {"Necessity": 0, "Want": 0, "Tithing":0}
        for spending in self.account.spendings:
            type_ = self.spending_type(spending)
            totals[type_] += spending.amount
        return totals


    def reccomended_spent(self):
        monthly_income = self.account.predicted_income
        return {"Necessity": monthly_income * BUDGET_RULE["Necessity"], "Want": monthly_income * BUDGET_RULE["Want"],
            "Saving": monthly_income * BUDGET_RULE["Saving"], "Tithing": monthly_income * BUDGET_RULE["Tithing"]}


    def generate_report(self):
        current = self.total_by_type()
        recommended = self.reccomended_spent()
        monthly_income = self.account.predicted_income
        report = []
        total_spending = 0
        for type in ["Necessity", "Want", "Tithing"]:
            difference = recommended[type] - current[type]
            total_spending += current[type]
            if difference < 0:
                report.append(f"You overspent on {type}s by ${(-difference):.2f}.")
            else:
                report.append(f"You are under your {type} budget by ${difference:.2f}.")
        report.append(f"It is recommended that you save ${recommended['Saving']:.2f} per month.")
        report.append(f"Currently, you are saving ${monthly_income - total_spending:.2f} per month.")
        if (monthly_income - total_spending) < (recommended['Saving']):
            report.append(f"You are currently saving ${(recommended['Saving'])-(monthly_income - total_spending)} than reccomended.")
        elif (monthly_income - total_spending) == (recommended['Saving']):
            report.append("You are meeting savings recommendations.")
        elif (monthly_income - total_spending) > (recommended['Saving']):
            report.append(f"You are currently saving ${(monthly_income - total_spending) - (recommended['Saving'])} more than reccomended.")
        return report
  
