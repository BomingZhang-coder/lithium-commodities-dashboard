import pandas as pd 

# Function to remove NaNs from a DataFrame 
def remove_nan(df):
    df = df.dropna(inplace = True)
    return df

def lag_column(df, column_name, new_column_name, lag):
    df[new_column_name] = df[column_name].shift(lag)
    return df
