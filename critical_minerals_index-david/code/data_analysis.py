import pandas as pd
from utilities import extract_metadata

def get_battery_minerals_costs(
    battery_minerals_required: pd.DataFrame, 
    mineral_spot_prices: pd.DataFrame,
    battery_market_shares: pd.DataFrame,
    metadata: dict
    ) -> pd.DataFrame:
    
    # Get metadata
    display, folders = extract_metadata(metadata)
    
    # Display debugging messages
    if display["debugging"]: 
        print("Getting battery mineral costs from battery minerals required, mineral spot prices, and battery market shares ...")
    
    # Convert the year index (currently an integer) to a datetime object
    battery_market_shares.index = pd.to_datetime(battery_market_shares.index, format = "%Y")
    
    # Extend the yearly market share data to be monthly 
    battery_market_share_expanded = battery_market_shares.reindex(mineral_spot_prices.index, method = "ffill")
    
    # Calculating the new dataframe with the scaled prices
    battery_minerals_costs = pd.DataFrame(index = mineral_spot_prices.index)
    for battery in battery_market_shares.columns:
        for mineral in battery_minerals_required.columns:
            battery_minerals_costs[(battery, mineral)] = (mineral_spot_prices[mineral] * battery_minerals_required.loc[battery, mineral] * battery_market_share_expanded[battery])
    
    battery_minerals_costs.columns = pd.MultiIndex.from_tuples(battery_minerals_costs.columns, names = ["battery", "mineral"])
    
    return battery_minerals_costs

def get_battery_costs(
    battery_minerals_costs: pd.DataFrame, 
    metadata: dict
) -> pd.DataFrame: 
    
    # Summing across the minerals to get the total cost to produce the battery 
    battery_costs = battery_minerals_costs.groupby(level = 0, axis = 1).sum()
    
    return battery_costs

def get_minerals_costs(
    battery_minerals_costs: pd.DataFrame, 
    metadata: dict
) -> pd.DataFrame: 
    
    # Grouping by the different minerals and summing them to get the total cost of each mineral across all batteries
    minerals_costs = battery_minerals_costs.groupby(level = 1, axis=1).sum()
    
    return minerals_costs

def get_minerals_market_share(
    minerals_costs: pd.DataFrame, 
    metadata:dict
) -> pd.DataFrame: 
    
    minerals_percentage_share = minerals_costs.div(minerals_costs.sum(axis = 1), axis = 0) * 100
    
    return minerals_percentage_share

def get_conglomerate_battery_cost(
    battery_costs: pd.DataFrame, 
    metadata: dict
    ) -> pd.DataFrame: 
    
    # Sum the rows 
    battery_costs["conglomerate_cost"] = battery_costs.sum(axis = 1)
    
    return battery_costs[["conglomerate_cost"]]

def get_battery_minerals_index(
    conglomerate_battery_cost: pd.DataFrame, 
    metadata: dict
) -> pd.DataFrame: 
    
    # Apply normalisation 
    battery_minerals_index = conglomerate_battery_cost / conglomerate_battery_cost.iloc[0] * 100
    
    return battery_minerals_index