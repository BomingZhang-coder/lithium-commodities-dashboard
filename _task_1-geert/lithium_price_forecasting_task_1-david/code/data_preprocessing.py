from datetime import datetime
import numpy as np
import pandas as pd
from utilities import remove_nan

# Function to get the spot prices of lithium carbonate from the raw csv file
def get_spot_prices(spot_prices_file):

    # Load as a dataframe 
    lithium_df = pd.read_csv(spot_prices_file)
    
    # Change column names
    lithium_df.columns = ["date", "spot_prices", "open", "high", "low", "volume", "percentage_change"]
    
    # Convert date column to be a datetime object
    lithium_df["date"] = pd.to_datetime(lithium_df["date"])
    
    # Set the index of the dataframe to be the dates
    lithium_df.set_index("date", inplace = True)
    
    # Sort the dataframe to be dates ascending
    lithium_df = lithium_df[["spot_prices"]].sort_index()
    
    # Convert the spot prices to be the float datatype
    lithium_df["spot_prices"] = lithium_df["spot_prices"].str.replace(",", "").astype(float)
    
    return lithium_df


# Function to calculate returns from spot prices
def get_returns(lithium_df):
    
    # Calculate returns
    lithium_df["returns"] = lithium_df["spot_prices"].pct_change()
    
    return lithium_df


# Function to calculate the natural log of the returns
def get_log_returns(lithium_df):
    
    # Calculate natural log of returns column
    lithium_df["log_returns"] = np.log(lithium_df["spot_prices"]).diff()
    
    return lithium_df


# Function to return the number of zeroes over the past 5 and 22 days
def count_zeroes(lithium_df, k_values):
    
    # Places a 0 if return value is not 0, and 1 if return value is 0
    lithium_df["is_zero"] = (lithium_df["log_returns"] == 0).astype(int)
    
    # Counts the number of zeroes in the past k days
    for k in k_values:
        lithium_df[f"zero_count_{k}"] = lithium_df["is_zero"].rolling(k).sum()
    
    return lithium_df


# Function to get the day of week for every day
def get_day_of_week(lithium_df):
    
    # Make a column for the day of the week
    lithium_df["day_of_week"] = lithium_df.index.day_name()
    
    return lithium_df
