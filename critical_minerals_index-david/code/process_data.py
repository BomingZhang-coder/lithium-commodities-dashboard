import pandas as pd

def get_amounts(batteries, average_battery_capacity):
    for battery in batteries: 
        for mineral, amount in battery.items():
            # Check if the amount is a list
            if isinstance(amount, list): 
                # Average numbers in the list
                battery[mineral] = sum(amount)/len(amount)
            battery[mineral] = battery[mineral] * average_battery_capacity / 1000 # Convert to tons
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