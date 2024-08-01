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




# This is terrible, convenient code. Needs fixing. 
def get_costs(minerals_required, spot_prices_df, battery_names):
    # Remove all rows where we have incomplete data
    spot_prices_df = spot_prices_df.dropna()
    
    cost_df = pd.DataFrame()
    
    name_index = 0
    for battery in minerals_required: 
        # Get the minerals required to make the battery
        minerals_list = battery.keys()
        # Filter spot prices to get just the spot prices of the minerals required to make the battery
        battery_cost_df = spot_prices_df[minerals_list]
        for mineral in minerals_list: 
            battery_cost_df[mineral] *= battery[mineral]
        battery_cost_df["total_cost"] = battery_cost_df.sum(axis = 1)
        #all_costs.append(battery_cost_df["total_cost"])
        cost_df[battery_names[name_index] + " Cathode + Anode Cost"] = battery_cost_df["total_cost"].round(2)
        name_index += 1
        
    return cost_df

def get_mineral_market_share(names, minerals_required_data, spot_prices_df, market_share_df):
    minerals_required_data.rename(index = names, inplace = True)
    
    years = market_share_df.index.tolist()
    
    scaled_minerals_required = pd.DataFrame(index = years)
    
    yearly_minerals_required = {}
    
    for year in years: 
        market_shares = market_share_df.loc[year]
        
        batteries = market_shares.index.tolist()
        
        minerals_required = []
        for battery in batteries: 
            if battery.lower() != "other":
                minerals_required.append(market_shares.loc[battery] * minerals_required_data.loc[battery])
                
        yearly_minerals_required[year] = minerals_required


    yearly_total_minerals_required = {}

    # Iterate through the dictionary
    for year, series_list in yearly_minerals_required.items():
        # Create an empty series to store the sum of minerals
        sum_series = pd.Series(dtype=float)
        for series in series_list:
            sum_series = sum_series.add(series, fill_value=0)
        
        yearly_total_minerals_required[year] = sum_series

    # Create a DataFrame from the dictionary
    mineral_share_df = pd.DataFrame(yearly_total_minerals_required).T
    
    # Display the DataFrame
    # print(mineral_share_df)
    # print(spot_prices_df.dropna())
    
    # Ensure columns match and fill any missing columns with zeroes
    required_minerals = mineral_share_df.columns
    spot_prices_df = spot_prices_df[required_minerals].fillna(0)

    # Function to get the requirement year from the date
    def get_requirement_year(date):
        return date.year

    # Apply the function to get the corresponding year requirements for each month
    years = spot_prices_df.index.year
    requirements_for_each_month = mineral_share_df.reindex(years).reset_index(drop=True)

    # Multiply each row by the corresponding year requirements to get individual mineral costs
    individual_costs = spot_prices_df.values * requirements_for_each_month.values

    # Create a DataFrame with the individual mineral costs and the corresponding dates
    df_individual_costs = pd.DataFrame(individual_costs, index=spot_prices_df.index, columns=spot_prices_df.columns)

    df_individual_costs.dropna(inplace = True)
    
    # Calculate the row-wise sum for each row
    row_sums = df_individual_costs.sum(axis=1)

    # Calculate the percentage for each mineral in each row
    percentage_df = df_individual_costs.div(row_sums, axis=0) * 100

    # Display the percentage dataframe
    return percentage_df