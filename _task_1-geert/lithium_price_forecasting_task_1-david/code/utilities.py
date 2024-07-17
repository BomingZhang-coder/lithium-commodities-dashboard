import numpy as np
import pandas as pd 

# Function to remove NaNs from a DataFrame 
def remove_nan(df):
    df = df.dropna(inplace = True)
    return df

# Function to lag a specific column and give it a new name 
def lag_column(df, column_name, new_column_name, lag):
    df[new_column_name] = df[column_name].shift(lag)
    return df

# Convert np floats to regular floats
def convert_floats(dictionary):
    output_dictionary = {}
    for day, dictionaries in dictionary.items():
        output_dictionary[day] = {k: float(v) for k, v in dictionaries.items()}
    return output_dictionary

# download dict as a csv via a dataframe
def download_results(results, name): 
    converted_results = convert_floats(results)
    results_df = pd.DataFrame.from_dict(converted_results, orient = "index")
    results_df.to_csv("output/" + name)