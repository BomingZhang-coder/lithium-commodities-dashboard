############### IMPORT EXTERNAL LIBRARIES ###############
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict
#########################################################

############### IMPORT INTERNAL LIBRARIES ###############
from utilities import get_filepath, extract_metadata
from plot_graphs import (
    plot_battery_mineral_requirements,
    plot_flakey_graphite_prices,
)
#########################################################

def get_battery_mineral_requirements(
    name: str, 
    metadata: dict
) -> pd.DataFrame:
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    if display["debugging"]:
        print("Getting battery mineral requirements from csv...")
    
    # Get the filepath for the battery mineral requirements
    filepath = get_filepath(folders["input"], name)
    
    # Convert from a csv to a DataFrame
    battery_minerals_required = pd.read_csv(filepath)
    
    # Make all the columns lowercase
    battery_minerals_required.columns = battery_minerals_required.columns.str.lower()
    
    # Set the battery type as the index
    battery_minerals_required.set_index("battery", inplace = True)
    
    # Convert the index to lowercase
    battery_minerals_required.index = battery_minerals_required.index.str.lower()
    
    # Function to average values containing commas
    def average_comma_values(val):
        if isinstance(val, str) and ',' in val:
            values = list(map(float, val.split(',')))
            return sum(values) / len(values)
        return val
    
    # Apply the function to each element in the dataframe
    battery_minerals_required = battery_minerals_required.applymap(average_comma_values)
    
    # Convert all the columns to floats
    battery_minerals_required = battery_minerals_required.astype(float)
    
    # Divide all the numbers by 1000 to get the minerals required in tons/kWh
    battery_minerals_required = battery_minerals_required / 1000
    
    if display["plots"]:
        plot_battery_mineral_requirements()
    
    return battery_minerals_required

def get_phosphorous_spot_prices(
    name: str, 
    metadata: dict
) -> pd.DataFrame: 
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    # Display debugging messages
    if display["debugging"]: 
        print("Getting phosphorous monthly spot prices from csv ...")
        
    # Get filepath for phosphorous csv
    phosphorous_spot_prices_filepath = get_filepath(folders["input"], name)
    
    phosphorous_df = pd.read_csv(phosphorous_spot_prices_filepath)
    
    # Rename columns
    phosphorous_df.columns = ["date", "phosphorous"]
    
    # Convert string to DateTime object
    phosphorous_df["date"] = pd.to_datetime(phosphorous_df["date"], format = "%b-%y")
    
    # Make sure prices are all numeric
    phosphorous_df["phosphorous"] = phosphorous_df["phosphorous"].astype(float)
    
    # Set the month and year to be the index
    phosphorous_df.set_index("date", inplace = True)
    
    # Sort the index ascending
    phosphorous_df.sort_index(ascending = True, inplace = True)
    
    return phosphorous_df

def get_flakey_graphite_prices(
    name: str, 
    metadata: dict
    ) -> pd.DataFrame:
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    # Display debugging messages
    if display["debugging"]: 
        print("Getting flakey graphite prices from csv ...")
    
    # Get the filepath for the flakey graphite prices
    filepath = get_filepath(folders["input"], name)
    
    # Read into a DataFrame from a csv file 
    graphite_prices_df = pd.read_csv(filepath)
    
    # Rename columns
    graphite_prices_df.columns = ["year", "flakey_graphite"]
    
    # Sort df by year 
    graphite_prices_df.sort_values(by = "year", inplace = True)
    
    # Set the year as the index
    graphite_prices_df.set_index("year", inplace = True)
    
    if display["plots"]:
        plot_flakey_graphite_prices(graphite_prices_df, folders["output"], name)
    
    return graphite_prices_df

def get_mineral_spot_prices(
    name: str, 
    metadata: dict
) -> pd.DataFrame: 
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    # Display debugging messages
    if display["debugging"]: 
        print("Getting mineral monthly spot prices from csv ...")
    
    # Get the filepath for the flakey graphite prices
    filepath = get_filepath(folders["input"], name)
    
    # Read the csv as a DataFrame
    spot_prices_df = pd.read_csv(filepath)
    
    # Make the columns all lowercase 
    spot_prices_df.columns = spot_prices_df.columns.str.lower()
    
    # Rename first column
    spot_prices_df.rename(columns = {"commodity name": "minerals"}, inplace = True)
    
    # Make the contents of the first column be all lower case
    spot_prices_df["minerals"] = spot_prices_df["minerals"].str.lower()
    
    # Set the minerals to be the index
    spot_prices_df.set_index("minerals", inplace = True)
    
    # Strip white spaces from the string index
    spot_prices_df.index = spot_prices_df.index.str.strip()
    
    # Transpose the DataFrame 
    spot_prices_df = spot_prices_df.T
    
    # Rename the index
    spot_prices_df.rename_axis("dates", inplace = True)
    
    # Convert the index to a datetime object
    spot_prices_df.index = pd.to_datetime(spot_prices_df.index, format = "%YM%m")
    
    # Get the phosphorous monthly spot prices
    phosphorous_spot_prices_df = get_phosphorous_spot_prices("Phosphorous Monthly Spot Prices", metadata)
    
    # Combine the phosphorous data with the rest of the minerals 
    spot_prices_df = spot_prices_df.join(phosphorous_spot_prices_df, how = "outer")
    
    # Get the yearly flakey graphite prices
    flakey_graphite_yearly_prices_df = get_flakey_graphite_prices("Flakey Graphite Yearly Prices", metadata)
    
    spot_prices_df["flakey_graphite"] = spot_prices_df.index.year.map(flakey_graphite_yearly_prices_df["flakey_graphite"].to_dict())
    
    # Remove all rows that have NaN in them 
    spot_prices_df.dropna(inplace = True)
    
    return spot_prices_df

def check_rows_sum_to_100(
    battery_market_share: pd.DataFrame
    ) -> bool:
    
    # Check if the sum of each row is equal to 100
    row_sums_equal_100 = (battery_market_share.sum(axis = 1) == 100)

    # Get the rows where the sum is not equal to 100
    rows_not_equal_100 = battery_market_share[~row_sums_equal_100]
    
    # Check if rows_not_equal_100 is empty
    if not rows_not_equal_100.empty:
        print("Some rows did not sum to 100!")
        print(rows_not_equal_100)
        return False
        quit()
    
    return True

def get_battery_market_shares(
    name: str, 
    metadata: dict
) -> pd.DataFrame:
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    # Display debugging messages
    if display["debugging"]: 
        print("Getting battery market share from csv ...")
    
    # Get the filepath for the flakey graphite prices
    filepath = get_filepath(folders["input"], name)
    
    # Read the csv as a DataFrame
    battery_market_share = pd.read_csv(filepath)
    
    # Make all the columns lowercase 
    battery_market_share.columns = battery_market_share.columns.str.lower()
    
    # Check if the 'other' batteries column is all 0
    if (battery_market_share["other"] == 0).all(): 
        battery_market_share.drop(["other"], axis = 1, inplace = True)
    
    # Set the date as the index
    battery_market_share.set_index("date", inplace = True)
    
    # Sort the DataFrame by the date
    battery_market_share.sort_index(ascending = True, inplace = True)
    
    # Do safety check that the rows of the market share sum to 100
    #check_rows_sum_to_100(battery_market_share)
    
    # Divide by 100 to get the fractions 
    battery_market_share = battery_market_share / 100
    
    return battery_market_share

def get_exchange_rates(
    exchange_rate_names: list,
    metadata: dict
    ) -> pd.DataFrame: 
    
    for exchange_rate_name in exchange_rate_names: 
        
        exchange_rate = pd.read_csv(f"datasets/macroeconomics/{exchange_rate_name}.csv")
        
        exchange_rate_name = exchange_rate_name.lower()
        exchange_rate.columns = ["date", exchange_rate_name]
        
        exchange_rate["date"] = pd.to_datetime(exchange_rate["date"])
        
        exchange_rate.set_index("date", inplace = True)
        
        # Convert the 'value' column to floats, replacing dots with NaNs
        exchange_rate[exchange_rate_name] = pd.to_numeric(exchange_rate[exchange_rate_name], errors = 'coerce')

        # Drop rows with NaNs 
        exchange_rate.dropna(inplace = True)
        
        exchange_rate_monthly = exchange_rate.resample("M").mean()
        
        # Adjust the index to show the first value of each month
        exchange_rate_monthly.index = exchange_rate_monthly.index.to_period('M').to_timestamp()
        
    return exchange_rate_monthly

def get_inflation_consumer_prices(
    inflation_list: list,
    metadata: dict
    ) -> pd.DataFrame: 
    
    for country in inflation_list: 
        
        inflation_country = pd.read_csv(f"datasets/macroeconomics/inflation_consumer_prices_{country}.csv")
        
        country_column = country.lower() + "_inflation"
        inflation_country.columns = ["date", country_column]
        
        inflation_country["date"] = pd.to_datetime(inflation_country["date"])
        
        inflation_country.set_index("date", inplace = True)
        
        inflation_country[country_column] = pd.to_numeric(inflation_country[country_column], errors = 'coerce')

        # Drop rows with NaNs 
        inflation_country.dropna(inplace = True)
    
        monthly_inflation_country = inflation_country.resample('M').ffill()
    
        # Adjust the index to show the first value of each month
        monthly_inflation_country.index = monthly_inflation_country.index.to_period('M').to_timestamp()
    
    return monthly_inflation_country

def get_google_trends_lithium(name, metadata): 
    
    google_trends_filepath = get_filepath("datasets/news", name)
    
    google_trends = pd.read_csv(google_trends_filepath)
    
    google_trends.columns = ["date", "google_trends_interest"]
    
    google_trends['date'] = pd.to_datetime(google_trends['date'], format='%Y-%m')
    
    google_trends.set_index("date", inplace = True)
    
    return google_trends