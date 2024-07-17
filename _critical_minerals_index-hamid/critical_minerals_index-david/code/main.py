from datetime import datetime
import pandas as pd 
import matplotlib.pyplot as plt
from process_data import get_amounts, get_imf_data, get_phosphate_data, get_costs
from plot_graphs import (
    plot_flakey_graphite_prices,
    plot_spot_prices, 
    plot_battery_cost, 
    plot_scaled_battery_cost,
    plot_conglomerated_scaled_cost, 
    plot_critical_minerals_index
)
from utilities import download_results

output_folder = "results"

# Dictionary containing the market share of various lithium-ion batteries from 2018 to 2023
market_share = {
    2018: {
        'NCA': 27.0,
        'NMC_standard': 11.5,
        'NMC_low_nickel': 50.8,
        'NMC_high_nickel': 1.6,
        'LFP': 9.1,
        'Other': 0.0
    },
    2019: {
        'NCA': 28.0,
        'NMC_standard': 6.6,
        'NMC_low_nickel': 53.0,
        'NMC_high_nickel': 5.7,
        'LFP': 6.7,
        'Other': 0.0
    },
    2020: {
        'NCA': 20.1,
        'NMC_standard': 5.1,
        'NMC_low_nickel': 44.3,
        'NMC_high_nickel': 18.9,
        'LFP': 11.6,
        'Other': 0.0
    },
    2021: {
        'NCA': 12.0,
        'NMC_standard': 3.3,
        'NMC_low_nickel': 28.8,
        'NMC_high_nickel': 29.9,
        'LFP': 26.0,
        'Other': 0.0
    },
    2022: {
        'NCA': 8.3,
        'NMC_standard': 2.0,
        'NMC_low_nickel': 19.8,
        'NMC_high_nickel': 34.3,
        'LFP': 35.6,
        'Other': 0.0
    },
    2023: {
        'NCA': 6.7,
        'NMC_standard': 1.0,
        'NMC_low_nickel': 17.8,
        'NMC_high_nickel': 34.8,
        'LFP': 39.7,
        'Other': 0.0
    }
}

# Dictionaries containing how much of each mineral is required in kg/kWh

NCA = {
    "lithium": 0.1, 
    "nickel": 0.71, 
    "cobalt": 0.13, 
    "aluminium": 0.02,
    "natural graphite": 1.2
}

LFP = {
    "lithium": 0.09, 
    "iron": 0.67, 
    "phosphorous": 0.37,
    "natural graphite": 1.2
}

# NMC-111, sometimes called NMC-333
NMC_standard = {
    "lithium": 0.14,
    "nickel": 0.35, 
    "cobalt": 0.35, 
    "manganese": 0.33, 
    "natural graphite": 1.2
}

# NMC-532/622
NMC_low_nickel = {
    "lithium": [0.11, 0.11], 
    "nickel": [0.47, 0.53], 
    "cobalt": [0.19, 0.18], 
    "manganese": [0.26, 0.17], 
    "natural graphite": [1.2, 1.2]
}

# NMC-721/811
NMC_high_nickel = {
    "lithium": [0.11, 0.1], 
    "nickel": [0.57, 0.66], 
    "cobalt": [0.17, 0.08], 
    "manganese": [0.08, 0.08], 
    "natural graphite": [1.2, 1.2]
}

# Price of flankey USD/ton
flakey_graphite_prices = {
    "2018": 1520, 
    "2019": 1340, 
    "2020": 1340, 
    "2021": 1390, 
    "2022": 1200, 
    "2023": 1200, 
    "2024": 1200 # Assuming it has stayed somewhat constant past 2023
}
flakey_graphite_prices_data = pd.DataFrame(list(flakey_graphite_prices.items()), columns=['Year', 'Price'])
name = "flakey_graphite_spot_prices"
download_results(flakey_graphite_prices_data, output_folder, name)
plot_flakey_graphite_prices(flakey_graphite_prices, output_folder, name)

# Names dictionary
names = {
}

# List of batteries we are interested in
batteries = {
    "NCA": NCA, 
    "LFP": LFP, 
    "Standard NMC (NMC-111)": NMC_standard, 
    "Low-nickel NMC (NMC-532/622)": NMC_low_nickel, 
    "High-nickel NMC (NMC-721/811)": NMC_high_nickel
}

battery_names = list(batteries.keys())
#print(battery_names)
battery_compositions = batteries.values()

# Average EV battery capacity in kWh
average_battery_capacity = 1 # kWh

# Scale the amount of each mineral by the average battery capacity to get amount required in ton
minerals_required = get_amounts(battery_compositions, average_battery_capacity)
minerals_required_data = pd.DataFrame(minerals_required, index = battery_names)

download_results(minerals_required_data, output_folder, "minerals_required_to_make_each_battery")

# Get mineral spot prices in USD/ton
imf_df = get_imf_data()
phosphate_df = get_phosphate_data()
spot_prices_df = imf_df.join(phosphate_df, how = "outer")
# Rename minerals column to match battery dictionaries
spot_prices_df.columns = ["nickel", "iron", "aluminium", "cobalt", "lithium", "manganese", "phosphorous", "silicon", "natural graphite"]
name = "spot_prices_of_all_minerals"
plot_spot_prices(spot_prices_df, "all", output_folder, name)
download_results(spot_prices_df, output_folder, name)

cost_df = get_costs(minerals_required, spot_prices_df, battery_names)
name = "cost_to_make_each_type_of_battery"
plot_battery_cost(cost_df, output_folder, name)
cost_df.columns = ["NCA", "LFP", "NMC_standard", "NMC_low_nickel", "NMC_high_nickel"]
cost_df["Year"] = cost_df.index.year
#print(cost_df)

# Market share of the different batteries from 2017 to 2023
market_share_df = pd.DataFrame.from_dict(market_share, orient = 'index') / 100

# save results of market share
name = "market_share_of_each_battery"
download_results(market_share_df, output_folder, name)
unique_years = market_share_df.index.unique().to_list()

filtered_cost_df = cost_df[cost_df["Year"].isin(unique_years)]
name = "cost_to_make_each_type_of_battery"
download_results(filtered_cost_df, output_folder, name)

critical_minerals_index = pd.DataFrame()
for column in filtered_cost_df.columns:
    if column != "Year":
        filtered_cost_df[column + "_market_share"] = filtered_cost_df["Year"].map(market_share_df[column])
        critical_minerals_index[column] = filtered_cost_df[column] * filtered_cost_df[column + "_market_share"]
# filtered_cost_df = filtered_cost_df.drop("Year", axis = 1)

name = "battery_costs_scaled_by_market_share"
plot_scaled_battery_cost(critical_minerals_index, output_folder, name)
download_results(critical_minerals_index, output_folder, name)

critical_minerals_index["Conglomerate Cost"] = critical_minerals_index.sum(axis = 1)
name = "conglomerate_cost_of_batteries"
download_results(critical_minerals_index, output_folder, name)
plot_conglomerated_scaled_cost(critical_minerals_index, output_folder, name)

normalisation_factor = critical_minerals_index["Conglomerate Cost"].iloc[0] / 100
critical_minerals_index["Index"] = critical_minerals_index["Conglomerate Cost"]/normalisation_factor
name = "critical_minerals_index"
download_results(critical_minerals_index["Index"], output_folder, name)
plot_critical_minerals_index(critical_minerals_index, output_folder, name)

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

plt.figure(figsize=(12, 12))
plt.grid()
plt.xlabel("Date")
plt.plot(critical_minerals_index.index, critical_minerals_index["Index"])
plt.scatter(datetime.strptime("2018-03-01", "%Y-%m-%d"), value_on_mar1, label = "Trump declares tariffs on steel and aluminium", color = "red")
plt.scatter(datetime.strptime("2020-01-01", "%Y-%m-%d"), value_on_jan20, label = "COVID announced", color = "orange")
plt.scatter(datetime.strptime("2022-02-24", "%Y-%m-%d"), value_near_feb24, label = "Russia invades Ukraine on Feb 24, 2022", color = "green")
plt.scatter(datetime.strptime("2023-03-28", "%Y-%m-%d"), value_on_mar28, label = "US and Japan sign critical minerals trade agreement", color = "blue")
plt.scatter(datetime.strptime("2023-10-07", "%Y-%m-%d"), value_on_oct23, label = "Israel-Hamas War", color = "purple")
plt.scatter(datetime.strptime("2023-12-13", "%Y-%m-%d"), value_on_dec13, label = "COP28 agrees on transition away from fossil fuels", color = "pink")
plt.title("Critical Minerals Index")
plt.legend()
plt.show()

# More analysis
#print(critical_minerals_index["Conglomerate Cost"])
#(spot_prices_df)

# Find percentage of each mineral in the critical minerals index

# Do a correlation study, i.e., plot the spot prices of each critical mineral 

# Goal: find the critical mineral that has the most impact