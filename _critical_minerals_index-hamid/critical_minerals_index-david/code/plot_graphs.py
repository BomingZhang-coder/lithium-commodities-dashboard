import pandas as pd
import matplotlib.pyplot as plt

def plot_spot_prices(minerals_df, graph_type):
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
    else: 
        print("Please double-check plot_spot_prices parameters.")
        return None

def plot_battery_cost(cost_df):
    plt.figure(figsize = (15, 15))
    for column in cost_df.columns.to_list():
        plt.plot(cost_df.index, cost_df[column], label = column)
    plt.grid()
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("USD$")
    #plt.title("Cost of Battery Cathode in Standard EV")
    plt.title("Cost of Raw Materials in Standard EV Cathode + Anode Scaled by Market Share")
    plt.show()