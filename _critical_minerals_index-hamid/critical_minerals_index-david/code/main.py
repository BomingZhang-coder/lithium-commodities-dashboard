import pandas as pd 
import matplotlib.pyplot as plt
from process_data import get_amounts, get_imf_data, get_phosphate_data, get_costs
from plot_graphs import plot_spot_prices, plot_battery_cost
from datetime import datetime

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
flakey_graphite_price = {
    "2018": 1520, 
    "2019": 1340, 
    "2020": 1340, 
    "2021": 1390, 
    "2022": 1200, 
    "2023": 1200, 
    "2024": 1200 # Assuming it has stayed somewhat constant past 2023
}

# # Extracting years and prices for plotting
# years = list(flakey_graphite_price.keys())
# prices = list(flakey_graphite_price.values())

# # Creating the scatter plot
# plt.figure(figsize=(10, 5))  # Set the figure size
# plt.plot(years, prices, color = 'blue')  # Plotting the points

# # Adding title and labels
# plt.title('Flakey Graphite Price Over Years')
# plt.xlabel('Year')
# plt.ylabel('Price (USD per ton)')

# # Optional: Add a grid for better readability
# plt.grid(True)

# # Show the plot
# plt.show()

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
print(battery_names)
battery_compositions = batteries.values()

# Average EV battery capacity in kWh
average_battery_capacity = 1 # kWh

# Scale the amount of each mineral by the average battery capacity to get amount required in ton
minerals_required = get_amounts(battery_compositions, average_battery_capacity)
#print(minerals_required)

# Get mineral spot prices in USD/ton
imf_df = get_imf_data()
phosphate_df = get_phosphate_data()
spot_prices_df = imf_df.join(phosphate_df, how = "outer")
# Rename minerals column to match battery dictionaries
spot_prices_df.columns = ["nickel", "iron", "aluminium", "cobalt", "lithium", "manganese", "phosphorous", "silicon", "natural graphite"]

plt.figure(figsize = (12, 12))
for column in spot_prices_df.columns.to_list():
    #print(column)
    # if column == "lithium" or column == "cobalt" or column == "nickel":
        
    # else:
    #     pass
    plt.plot(spot_prices_df.index, spot_prices_df[column], label = column)
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylabel("Price (USD per ton)")
plt.title("Mineral Price change over time")
plt.savefig("mineral_prices")
#plt.show()

cost_df = get_costs(minerals_required, spot_prices_df, battery_names)
#plot_battery_cost(cost_df)
cost_df.columns = ["NCA", "LFP", "NMC_standard", "NMC_low_nickel", "NMC_high_nickel"]
cost_df["Year"] = cost_df.index.year
#print(cost_df)

# Market share of the different batteries from 2017 to 2023
market_share_df = pd.DataFrame.from_dict(market_share, orient = 'index') / 100
#print(market_share_df)
unique_years = market_share_df.index.unique().to_list()

filtered_cost_df = cost_df[cost_df["Year"].isin(unique_years)]

critical_minerals_index = pd.DataFrame()
for column in filtered_cost_df.columns:
    if column != "Year":
        filtered_cost_df[column + "_market_share"] = filtered_cost_df["Year"].map(market_share_df[column])
        critical_minerals_index[column] = filtered_cost_df[column] * filtered_cost_df[column + "_market_share"]
# filtered_cost_df = filtered_cost_df.drop("Year", axis = 1)
#plot_battery_cost(critical_minerals_index)

critical_minerals_index["Conglomerate Cost"] = critical_minerals_index.sum(axis = 1)
plt.figure(figsize=(12, 12))
plt.grid()
plt.xlabel("Date")
plt.ylabel("USD$")
plt.plot(critical_minerals_index.index, critical_minerals_index["Conglomerate Cost"])
plt.title("Conglomerated Scaled Cost of Battery Cathode + Anode in Standard EV")
plt.show()

normalisation_factor = critical_minerals_index["Conglomerate Cost"].iloc[0] / 100
critical_minerals_index["Index"] = critical_minerals_index["Conglomerate Cost"]/normalisation_factor

critical_minerals_index["Index"].to_csv("Critical Minerals Index.csv")

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

# plt.figure(figsize=(12, 12))
# plt.grid()
# plt.xlabel("Date")
# plt.plot(critical_minerals_index.index, critical_minerals_index["Index"])
# plt.scatter(datetime.strptime("2018-03-01", "%Y-%m-%d"), value_on_mar1, label = "Trump declares tariffs on steel and aluminium", color = "red")
# plt.scatter(datetime.strptime("2020-01-01", "%Y-%m-%d"), value_on_jan20, label = "COVID announced", color = "orange")
# plt.scatter(datetime.strptime("2022-02-24", "%Y-%m-%d"), value_near_feb24, label = "Russia invades Ukraine on Feb 24, 2022", color = "green")
# plt.scatter(datetime.strptime("2023-03-28", "%Y-%m-%d"), value_on_mar28, label = "US and Japan sign critical minerals trade agreement", color = "blue")
# plt.scatter(datetime.strptime("2023-10-07", "%Y-%m-%d"), value_on_oct23, label = "Israel-Hamas War", color = "purple")
# plt.scatter(datetime.strptime("2023-12-13", "%Y-%m-%d"), value_on_dec13, label = "COP28 agrees on transition away from fossil fuels", color = "pink")
# plt.title("Critical Minerals Index")
# plt.legend()
# plt.show()