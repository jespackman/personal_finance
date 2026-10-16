from datetime import date
from Account import Account
from Bill import Bill


def due_dates(bill, count):
    dates = []
    for _ in range(count):
        dates.append(bill.due_date)
        bill = bill.next_due()
    return dates


def test_monthly_bill_keeps_its_day():
    bill = Bill("Phone", 50, date(2026, 3, 15), recurring=True, monthly=True)
    assert due_dates(bill, 3) == [date(2026, 3, 15), date(2026, 4, 15), date(2026, 5, 15)]


def test_monthly_bill_on_the_31st_uses_month_end_then_returns():
    bill = Bill("Rent", 900, date(2026, 1, 31), recurring=True, monthly=True)
    assert due_dates(bill, 4) == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30)]


def test_monthly_bill_rolls_over_the_year():
    bill = Bill("Gym", 20, date(2026, 12, 15), recurring=True, monthly=True)
    assert bill.next_due().due_date == date(2027, 1, 15)


def test_every_x_days_bill():
    bill = Bill("Cleaner", 40, date(2026, 1, 1), recurring=True, frequency=14)
    assert due_dates(bill, 3) == [date(2026, 1, 1), date(2026, 1, 15), date(2026, 1, 29)]


def test_missed_monthly_bills_are_all_charged():
    account = Account("A", "1")
    account.add_bill("Rent", 900, date(2026, 1, 31), recurring=True, monthly=True)
    account.update_balance(date(2026, 5, 1))
    assert account.balance == -3600
    assert account.bills[0].due_date == date(2026, 5, 31)


def test_monthly_survives_saving():
    bill = Bill.from_dict(Bill("Rent", 900, date(2026, 2, 28), recurring=True, monthly=True, day_of_month=31).to_dict())
    assert bill.monthly and bill.day_of_month == 31
    assert bill.next_due().due_date == date(2026, 3, 31)


def test_bills_saved_before_monthly_existed_still_load():
    bill = Bill.from_dict({"name": "Old", "amount": 5, "due_date": "2026-02-10", "recurring": True, "frequency": 30})
    assert bill.recurrence() == "Every 30 days"
