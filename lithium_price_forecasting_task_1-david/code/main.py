from data_preprocessing import (
    get_spot_prices, 
    get_returns, 
    get_log_returns, 
    count_zeroes,
    get_day_of_week
)
from data_analysis import (
    get_weekly_data, 
    rescale_zeroes,
    rename_columns,
    get_lags, 
    get_multiplied_columns, 
    add_constant_column
)
from data_modelling import get_model
from utilities import remove_nan


#########################################################
#################### DATA PROCESSING ####################
#########################################################

# Website to attain lithium carbonate spot prices: "https://www.investing.com/commodities/lithium-carbonate-99-min-china-futures-historical-data"
# Raw lithium carbonate 99% china spot prices file path
lithium_spot_file = "datasets/wind_lithium_carbonate_spot_prices.csv"

# Get spot prices of lithium carbonate
lithium_df = get_spot_prices(lithium_spot_file)

# Get the returns of spot prices
lithium_df = get_returns(lithium_df)

# Get the log value of returns 
lithium_df = get_log_returns(lithium_df)

# Define the k values which are mentioned in the various models
k_values = (5, 10, 22)

# Get the number of zero returns in the past k days
lithium_df = count_zeroes(lithium_df, k_values)

# Get the day of week of each day
lithium_df = get_day_of_week(lithium_df)

# Get rid of values that are not numbers
remove_nan(lithium_df)


#########################################################
##################### DATA ANALYSIS #####################
#########################################################

# Split the lithium data into separate data for friday, monday, ..., thursday
weekly_data = get_weekly_data(lithium_df, k_values)

# Create new columns for re-scaling zero count
weekly_data = rescale_zeroes(weekly_data, k_values)

# Rename columns to match professor's specifications
new_column_names = {
    "log_returns": "r(t)",
}
weekly_data = rename_columns(weekly_data, new_column_names)

# Get the required lags for all the columns
weekly_data = get_lags(weekly_data, k_values)

# Multiply required columns together
for k in k_values:  
    weekly_data = get_multiplied_columns(weekly_data, f"z(t-1,{k})", "r(t-1)")
    weekly_data = get_multiplied_columns(weekly_data, f"z(t-2,{k})", "r(t-2)")

# Add a constant column to all the dataframes
weekly_data = add_constant_column(weekly_data)

# # Print out the first 10 rows for fridays
# print(weekly_data["fridays"].head(10))
# # Print out the columns for the fridays data
# print(weekly_data["fridays"].columns)

#########################################################
#################### DATA MODELLING #####################
#########################################################

# Constants to be found for new models 1. and 2. 
constants = {
    "alpha(0)": "alpha(0)",
    "phi(1,0)": "r(t-1)",
    "phi(1,1)": "z(t-1,k)*r(t-1)",
    "phi(2,0)": "r(t-2)",
    "phi(2,1)": "z(t-2,k)*r(t-2)"
}
columns = list(constants.values())

# New model 1. 
k_values = (5, 22)
for k in k_values:
    X = [column.replace('k', str(k)) for column in columns]
    y = "r(t)"
    model = get_model(weekly_data, X, y)
    
# New model 2. 
k = 10
X = [column.replace('k', str(k)) for column in columns]
y = "r(t)"
model = get_model(weekly_data, X, y)

# constants = {
#     "alpha(0)": "alpha(0)",
#     "phi": 
# }