import pandas as pd
import matplotlib.pyplot as plt

def plot_flakey_graphite_prices(flakey_graphite_price, output, name):
    # Extracting years and prices for plotting
    years = list(flakey_graphite_price.keys())
    prices = list(flakey_graphite_price.values())

    # Creating the scatter plot
    plt.figure(figsize=(10, 5))  # Set the figure size
    plt.plot(years, prices, color = 'blue')  # Plotting the points

    # Adding title and labels
    plt.title('Flakey Graphite Price Over Years')
    plt.xlabel('Year')
    plt.ylabel('Price (USD per ton)')

    # Optional: Add a grid for better readability
    plt.grid(True)
    
    # Save plot as png
    plt.savefig(f"{output}/{name}.png")

    # Show the plot
    plt.show()

def plot_spot_prices(minerals_df, graph_type, output, name):
    # If we plot spot prices in separate graphs
    if graph_type == "separate": 
        for column in minerals_df.columns.to_list():
            plt.figure(figsize = (15, 15))
            plt.plot(minerals_df.index, minerals_df[column], label = column)
            plt.grid()
            plt.legend()
            plt.xlabel("Date")
            plt.ylabel("Price (USD per ton)")
            plt.title("Mineral Price change over time")
            plt.savefig("mineral_prices")
            plt.show()
    # If we plot spot prices all in one graph
    elif graph_type == "all": 
        plt.figure(figsize = (15, 15))
        for column in minerals_df.columns.to_list():
            plt.plot(minerals_df.index, minerals_df[column], label = column)
        plt.grid()
        plt.legend()
        plt.xlabel("Date")
        plt.ylabel("Price (USD per ton)")
        plt.title("Mineral Price change over time")
        # Save plot as png
        plt.savefig(f"{output}/{name}.png")
        plt.show()
    else: 
        print("Please double-check plot_spot_prices parameters.")
        return None

def plot_battery_cost(cost_df, output, name):
    plt.figure(figsize = (15, 15))
    for column in cost_df.columns.to_list():
        plt.plot(cost_df.index, cost_df[column], label = column)
    plt.grid()
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("USD$")
    #plt.title("Cost of Battery Cathode in Standard EV")
    plt.title("Cost of Raw Materials to produce Cathode + Anode for 1 kWh")
    # Save plot as png
    plt.savefig(f"{output}/{name}.png")
    plt.show()

def plot_scaled_battery_cost(cost_df, output, name):
    plt.figure(figsize = (15, 15))
    for column in cost_df.columns.to_list():
        plt.plot(cost_df.index, cost_df[column], label = column)
    plt.grid()
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("USD$")
    #plt.title("Cost of Battery Cathode in Standard EV")
    plt.title("Cost of Raw Materials to produce Cathode + Anode for 1 kWh Scaled by Market Share")
    # Save plot as png
    plt.savefig(f"{output}/{name}.png")
    plt.show()
    
def plot_conglomerated_scaled_cost(critical_minerals_index, output, name):
    plt.figure(figsize=(12, 12))
    plt.grid()
    plt.xlabel("Date")
    plt.ylabel("USD$")
    plt.plot(critical_minerals_index.index, critical_minerals_index["Conglomerate Cost"])
    plt.title("Conglomerated Scaled Cost of Battery Cathode + Anode to produce 1 kWh")
    # Save plot as png
    plt.savefig(f"{output}/{name}.png")
    plt.show()

def plot_critical_minerals_index(critical_minerals_index, output, name):
    plt.figure(figsize=(18, 12))
    plt.grid()
    plt.xlabel("Date")
    plt.ylabel("Index relative to 100 since beginning")
    plt.plot(critical_minerals_index.index, critical_minerals_index["Index"])
    plt.title("Critical Minerals Index")
    # Save plot as png
    plt.savefig(f"{output}/{name}.png")
    plt.show()