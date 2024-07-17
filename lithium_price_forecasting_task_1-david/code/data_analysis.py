import datetime as datetime
import numpy as np
import pandas as pd
from utilities import remove_nan, lag_column


# Function to split the lithium data into different dataframes for friday, monday, ..., thursday
def get_weekly_data(lithium_df, k_values): 
    
    # List of groupings for every trading day
    groupings = {
        "fridays": "W-FRI",    # Weekly, Friday
        "mondays": "W-MON",    # Weekly, Monday
        "tuesdays": "W-TUE",   # Weekly, Tuesday
        "wednesdays": "W-WED", # Weekly, Wednesday
        "thursdays": "W-THU"   # Weekly, Thursday
    }
    
    # Create aggregation rules so new weekly dataframes know what to do with old columns
    aggregation_rules = {
        "log_returns": "sum", # We want to sum the log returns
    }
    for k in k_values:
        aggregation_rules[f"zero_count_{k}"] = "last" # We want the number of zeroes on the specific day
    
    # Split the data accordingly
    weekly_data = {}
    for day_of_week, grouping in groupings.items(): 
        weekly_data[day_of_week] = lithium_df.groupby(pd.Grouper(freq = grouping)).agg(aggregation_rules)
    
    return weekly_data


# Function to re-scale the zero count by 5 and 22, respectively
def rescale_zeroes(weekly_data, k_values):
    
    # Divide count by k
    for day, data in weekly_data.items():
        for k in k_values:
            data[f"z(t,{k})"] = data[f"zero_count_{k}"] / k
    
    return weekly_data


# Function to rename columns
def rename_columns(weekly_data, rename_dict):
    
    # Rename all the individual dataframe column names
    for day, data in weekly_data.items():
        data.rename(columns = rename_dict, inplace = True)
        
    return weekly_data

# Funciton to get the necessary lags for all the columns
def get_lags(weekly_data, k_values):
    
    # Get all the necessary lags for the required models
    for day, data in weekly_data.items(): 
        shift_values = (1, 2)
        for shift_value in shift_values: 
            data[f"r(t-{shift_value})"] = data["r(t)"].shift(shift_value)
            for k in k_values: 
                data[f"z(t-{shift_value},{k})"] = data[f"z(t,{k})"].shift(shift_value)
        
        # Remove all rows that contain values that are not numbers
        remove_nan(data)
        
    return weekly_data


# Function to multiple columns together
def get_multiplied_columns(weekly_data, column_name_1, column_name_2):
    
    # Create a new column that multiplies two columns together
    for day, data in weekly_data.items():
        multiplied_column_name = column_name_1 + "*" + column_name_2
        data[multiplied_column_name] = data[column_name_1] * data[column_name_2]
    
    return weekly_data

# Function to add a constant column to all dataframes
def add_constant_column(weekly_data): 
    for days, data in weekly_data.items():
        data["alpha(0)"] = 1
    return weekly_data

# Function to generate x(t-1)
def get_logistic_column(weekly_data):
    for days, data in weekly_data.items():
        data
    return weekly_data