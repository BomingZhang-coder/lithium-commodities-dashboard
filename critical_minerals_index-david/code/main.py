############### IMPORT EXTERNAL LIBRARIES ###############
from datetime import datetime
import pandas as pd 
import matplotlib.pyplot as plt
#########################################################

############### IMPORT INTERNAL LIBRARIES ###############
from data_collection_cleaning import (
    get_battery_mineral_requirements,
    get_mineral_spot_prices,
    get_battery_market_shares, 
    # Functions for extracting macroeconomic data
    get_exchange_rates,
    get_inflation_consumer_prices,
    # Functions for extracting lithium-related news
    get_google_trends_lithium
)
from data_analysis import (
    get_battery_minerals_costs,
    get_battery_costs,
    get_minerals_costs,
    get_minerals_market_share,
    get_conglomerate_battery_cost,
    get_battery_minerals_index
)
from data_modelling import (
    get_modelling_data,
    model_lithium_market_share,
    #get_linear_regression_parameters
)
from utilities import (
    compress_metadata,
    download_results
)
#########################################################

#################### DEFINE METADATA ####################
# Decide whether to show graphs and debugging messages
display = {
    "plots": False,
    "debugging": True,
}

# Define names of input and output folders for datasets and graphs
folders = {
    "input": "datasets",
    "output": "results"
}

# Decide whether to use interpolation on yearly data
interpolation = {
    "spline": True,
    "polynomial": False
}

# Compress above metadata about displaying things and folder names into a dictionary
metadata = compress_metadata(display, folders, interpolation)
#########################################################

#################### DATA COLLECTION ####################
# Get the minerals required to make each type of battery in the form of a DataFrame
battery_mineral_requirements = get_battery_mineral_requirements("Battery Mineral Requirements", metadata)

# Get the mineral spot prices in the form of a DataFrame
minerals_monthly_spot_prices = get_mineral_spot_prices("Mineral Monthly Spot Prices", metadata)

# Get the market share of the batteries 
battery_yearly_market_shares = get_battery_market_shares("Battery Yearly Market Shares", metadata)

## Get macroeconomic data
# Get exchange rate data
exchange_rate_list = [
    "CNY_to_USD", 
    #"CNY_to_EUR",
    #"USD_to_EUR"
]
exchange_rates = get_exchange_rates(exchange_rate_list, metadata)

inflation_list = [
    "china",
    #"usa", 
    #"europe"
]
inflation_consumer_prices = get_inflation_consumer_prices(inflation_list, metadata)

## Get news data
google_trends_lithium = get_google_trends_lithium("Google Trends Lithium Worldwide News", metadata)
#########################################################

##################### DATA ANALYSIS #####################
# Get the monthly cost of each mineral in each type of battery 
battery_minerals_monthly_costs = get_battery_minerals_costs(
    battery_mineral_requirements, 
    minerals_monthly_spot_prices, 
    battery_yearly_market_shares, 
    metadata
    )

# Get the monthly cost to produce each type of battery, scaled by their market share, by summing the monthly mineral costs 
battery_monthly_costs = get_battery_costs(battery_minerals_monthly_costs, metadata)

# Get the monthly cost of each different mineral to produce the different batteries 
minerals_monthly_costs = get_minerals_costs(battery_minerals_monthly_costs, metadata)

# Get the monthly market share of each mineral 
minerals_market_share = get_minerals_market_share(minerals_monthly_costs, metadata)

# Get the conglomerate cost to produce each type of battery, scaled by their market share
conglomerate_battery_monthly_cost = get_conglomerate_battery_cost(battery_monthly_costs, metadata)

# Normalise everything, setting the first instance to be 100
battery_minerals_index = get_battery_minerals_index(conglomerate_battery_monthly_cost, metadata)
#########################################################

##################### DATA MODELLING ####################
# Implement a dictionary structure for the specific data we want in the future
modelling_data_specifications = {
    "data": ["column1", "column2"]
}
modelling_data = get_modelling_data(
    minerals_market_share,        # Get Lithium market share 
    battery_yearly_market_shares, # Get the market share of LFP 
    minerals_monthly_spot_prices, # Get Lithium spot prices 
    exchange_rates, 
    inflation_consumer_prices,
    google_trends_lithium,
    metadata
)

results = model_lithium_market_share(modelling_data, metadata)

# linear_regression_parameters = get_linear_regression_parameters(results)
# print(linear_regression_parameters)
#########################################################

##################### MISCELLANEOUS #####################
events = {
    "2022-02-24": "Russia Invades Ukraine", 
    "2020-01-01": "COVID Announced", 
    "2023-03-28": "US and Japan Sign Critical Minerals Agreement Act", 
    "2023-10-23": "Israel-Hamas war",
    "2023-12-13": "COP28 UN Climate Change Conference", 
    "2018-03-01": "Trump Declares Tariffs on Steel and Aluminium"
}
#########################################################