import numpy as np
import pandas as pd
import statsmodels.api as sm

def get_model(weekly_data, X, y):
    for day, data in weekly_data.items():
        model = sm.OLS(data[y], data[X]).fit()
        print("Results for " + day)
        print(model.summary())