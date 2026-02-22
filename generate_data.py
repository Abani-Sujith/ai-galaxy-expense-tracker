import pandas as pd
import random
from datetime import datetime, timedelta

FILE_PATH = "data/expenses.csv"

categories = ["Food", "Travel", "Bills", "Shopping", "Other"]

start_date = datetime(2024, 1, 1)
days = 365

data = []

for i in range(days):
    date = start_date + timedelta(days=i)

    # Random number of expenses per day
    for _ in range(random.randint(1, 3)):

        category = random.choice(categories)

        if category == "Food":
            amount = random.randint(100, 600)
        elif category == "Travel":
            amount = random.randint(50, 400)
        elif category == "Bills":
            amount = random.randint(500, 3000)
        elif category == "Shopping":
            amount = random.randint(300, 5000)
        else:
            amount = random.randint(100, 1000)

        description = f"{category} expense"

        data.append([date.strftime("%Y-%m-%d"), amount, category, description])

df = pd.DataFrame(data, columns=["Date", "Amount", "Category", "Description"])

df.to_csv(FILE_PATH, index=False)

print("1 Year realistic expense data generated successfully!")