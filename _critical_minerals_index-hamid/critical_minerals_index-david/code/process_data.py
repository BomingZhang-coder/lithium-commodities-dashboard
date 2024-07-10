import pandas as pd

def get_amounts(batteries, average_battery_capacity):
    for battery in batteries: 
        for mineral, amount in battery.items():
            # Check if the amount is a list
            if isinstance(amount, list): 
                # Average numbers in the list
                battery[mineral] = sum(amount)/len(amount)
            battery[mineral] = battery[mineral] * average_battery_capacity / 1000
    return batteries

# Function to extract IMF data about mineral spot prices
def get_imf_data():
  # Get the DataFrame from the IMF data and transpose the csv
  conglomerate_df = pd.read_csv("datasets/conglomerate_mineral_data.csv").T
  # Clean and rename columns
  conglomerate_columns = conglomerate_df.iloc[0]
  conglomerate_columns = [column.lower().strip() for column in conglomerate_columns]
  conglomerate_df.columns = conglomerate_columns
  conglomerate_df = conglomerate_df.iloc[1:]
  conglomerate_df = conglomerate_df.astype(float)
  # Convert index to use datetime objects
  conglomerate_df.index = pd.to_datetime(conglomerate_df.index, format = "%YM%m")
  return conglomerate_df

def get_phosphate_data():
  phosphate_df = pd.read_csv("datasets/phosphate.csv")
  # Rename columns
  phosphate_df.columns = ["date", "phosphate"]
  # Convert string to DateTime object
  phosphate_df["date"] = pd.to_datetime(phosphate_df["date"], format = "%b-%y")
  # Make sure prices are all numeric
  phosphate_df["phosphate"] = phosphate_df["phosphate"].astype(float)
  # Set the month and year to be the index
  phosphate_df = phosphate_df.set_index("date")
  return phosphate_df

# This is terrible, convenient code. Needs fixing. 
def get_costs(minerals_required, spot_prices_df, battery_names):
    # Remove all rows where we have incomplete data
    spot_prices_df = spot_prices_df.dropna()
    
    cost_df = pd.DataFrame()
    
    all_costs = []
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
        cost_df[battery_names[name_index] + " Cathode Cost"] = battery_cost_df["total_cost"].round(2)
        name_index += 1
        
    return cost_df