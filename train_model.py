import pandas as pd
import os
import joblib
from statsmodels.tsa.arima.model import ARIMA

FILE_PATH = "data/expenses.csv"
MODEL_PATH = "expense_model.pkl"

if os.path.exists(FILE_PATH):

    df = pd.read_csv(FILE_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    # Monthly totals
    df["Month"] = df["Date"].dt.to_period("M")
    monthly = df.groupby("Month")["Amount"].sum()
    monthly.index = monthly.index.to_timestamp()

    # Need at least 3 months of data
    if len(monthly) < 3:
        print("Need at least 3 months of data for ARIMA.")
    else:
        model = ARIMA(monthly, order=(1,1,1))
        model_fit = model.fit()

        joblib.dump(model_fit, MODEL_PATH)
        print("ARIMA model trained and saved successfully!")

else:
    print("No expense data found.")