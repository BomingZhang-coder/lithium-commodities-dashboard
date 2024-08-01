import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from utilities import get_filepath

def plot_battery_mineral_requirements():
    # Code for stacked bar chart plot 
    return

def plot_flakey_graphite_prices(
    flakey_graphite_df: pd.DataFrame, 
    output_folder: str, 
    name: str
    ) -> None:
    
    # Creating the plot 
    plt.figure(figsize = (10, 5))  # Set the figure size
    plt.plot(flakey_graphite_df.index, flakey_graphite_df, color = 'blue')  # Plotting the points

    # Adding title and labels
    plt.title('Flakey Graphite Price Over Years')
    plt.xlabel('Year')
    plt.ylabel('Price (USD per ton)')

    # Adding a grid for better visibility
    plt.grid(True)
    plt.savefig(f"{output_folder}/{name}.png")

    # Display the graph
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


def plot_normalised_data(scaled_data):
    # Define a list of colors
    colors = list(mcolors.TABLEAU_COLORS.values())

    # Create a figure and a grid of subplots
    num_columns = len(scaled_data.columns) - 1  # Excluding "Conglomerate Cost"
    fig, axes = plt.subplots(num_columns, 1, figsize=(18, 12), sharex=True)
    
    # If there's only one subplot, convert axes to a list for consistency
    if num_columns == 1:
        axes = [axes]
    
    # Plot "Conglomerate Cost" on each subplot for reference
    for ax in axes:
        ax.plot(scaled_data.index, scaled_data["Conglomerate Cost"], linewidth=1.5, label="Conglomerate Cost", color="black", zorder=2)

    # Plot other columns on their respective subplots
    subplot_index = 0
    for i, column in enumerate(scaled_data.columns):
        if column != "Conglomerate Cost":
            color = colors[i % len(colors)]  # Cycle through the colors
            axes[subplot_index].plot(scaled_data.index, scaled_data[column], label=column, color=color, zorder=1)
            axes[subplot_index].set_ylabel("z-score")
            axes[subplot_index].legend()
            axes[subplot_index].grid()
            subplot_index += 1

    # Set common labels and title
    axes[-1].set_xlabel("Date")
    fig.suptitle("Critical Minerals Index")

    # Show the plot
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)  # Adjust the top for the suptitle
    plt.show()

def plot_mineral_percentages(percentage_df, output, name):
    # Plotting stacked bar chart
    ax = percentage_df.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage')
    ax.set_title('Percentage of Each Mineral Over Time')
    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in percentage_df.index], rotation=45, ha='right')

    plt.tight_layout()
    plt.show()
    plt.savefig(f"{output}/{name}.png")
    plt.show()

# def plot_events_critical_minerals(critical_minerals_index, values):
    
#     plt.figure(figsize=(12, 12))
#     plt.grid()
#     plt.xlabel("Date")
#     plt.plot(critical_minerals_index.index, critical_minerals_index["Index"])
#     plt.scatter(datetime.strptime("2018-03-01", "%Y-%m-%d"), value_on_mar1, label = "Trump declares tariffs on steel and aluminium", color = "red")
#     plt.scatter(datetime.strptime("2020-01-01", "%Y-%m-%d"), value_on_jan20, label = "COVID announced", color = "orange")
#     plt.scatter(datetime.strptime("2022-02-24", "%Y-%m-%d"), value_near_feb24, label = "Russia invades Ukraine on Feb 24, 2022", color = "green")
#     plt.scatter(datetime.strptime("2023-03-28", "%Y-%m-%d"), value_on_mar28, label = "US and Japan sign critical minerals trade agreement", color = "blue")
#     plt.scatter(datetime.strptime("2023-10-07", "%Y-%m-%d"), value_on_oct23, label = "Israel-Hamas War", color = "purple")
#     plt.scatter(datetime.strptime("2023-12-13", "%Y-%m-%d"), value_on_dec13, label = "COP28 agrees on transition away from fossil fuels", color = "pink")
#     plt.title("Critical Minerals Index")
#     plt.legend()
#     plt.show()