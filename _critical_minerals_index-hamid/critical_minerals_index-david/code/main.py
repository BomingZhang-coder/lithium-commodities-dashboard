############### IMPORT EXTERNAL LIBRARIES ###############
from datetime import datetime
import pandas as pd 
import matplotlib.pyplot as plt
#########################################################

############### IMPORT INTERNAL LIBRARIES ###############
from data_collection_cleaning import (
    get_battery_mineral_requirements,
    get_mineral_spot_prices,
    get_battery_market_shares
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
    get_lithium_market_share_data,
    model_lithium_market_share,
    get_linear_regression_parameters
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

# Compress above metadata about displaying things and folder names into a dictionary
metadata = compress_metadata(display, folders)
#########################################################

#################### DATA COLLECTION ####################
# Get the minerals required to make each type of battery in the form of a DataFrame
battery_mineral_requirements = get_battery_mineral_requirements("Battery Mineral Requirements", metadata)

# Get the mineral spot prices in the form of a DataFrame
minerals_monthly_spot_prices = get_mineral_spot_prices("Mineral Monthly Spot Prices", metadata)

# Get the market share of the batteries 
battery_yearly_market_shares = get_battery_market_shares("Battery Yearly Market Shares", metadata)
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
lithium_market_share_data = get_lithium_market_share_data(
    minerals_market_share, 
    battery_yearly_market_shares, 
    minerals_monthly_spot_prices, 
    metadata
)

results = model_lithium_market_share(lithium_market_share_data, metadata)
print(results)

linear_regression_parameters = get_linear_regression_parameters(results)
print(linear_regression_parameters)
#########################################################
quit()

#print(critical_minerals_index)
# Russia invades Ukraine on Feb 24, 2022
value_near_feb24 = critical_minerals_index["Index"].loc["2022-03-01"]

# COVID announced
value_on_jan20 = critical_minerals_index["Index"].loc["2020-01-01"]

# US and Japan sign critical minerals agreement act
value_on_mar28 = critical_minerals_index["Index"].loc["2023-04-01"]

# Israel-Hamas war
value_on_oct23 = critical_minerals_index["Index"].loc["2023-10-01"]

# COP28 UN Climate Change Conference
value_on_dec13 = critical_minerals_index["Index"].loc["2023-12-01"]

# Trump declares tariffs on steel and aluminium
value_on_mar1 = critical_minerals_index["Index"].loc["2018-03-01"]

"""
Dr Hamid's instructions from meeting 
If LFP increases from 40% to 60%, then what happens to the share of lithium in the BMI? 
Forecast this ^ 
Make the assumption that LFP in the next 2 years goes from 40% to 60% 
This will give a forecasted share of lithium demand 
We know the BMI is normalised to 1 kWh
What is the projected battery capacity in 2030? 
If we know total, and we know LFP is 60% of that, from there we can derive the total lithium needed
"""
"""
Questions/Notes: 
- What about the price of lithium? Would we have to forecast the price of lithium? 
- Find the mineral concentration of each battery - Dr Hamid claims that LFP is much 'denser' in lithium - add this to dashboard? 
- 
"""