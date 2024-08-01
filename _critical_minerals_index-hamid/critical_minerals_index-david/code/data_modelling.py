import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def get_lithium_market_share_data(
    minerals_market_share: pd.DataFrame, 
    battery_yearly_market_shares: pd.DataFrame, 
    minerals_monthly_spot_prices: pd.DataFrame,
    metadata
) -> pd.DataFrame: 
    
    # Create a DataFrame to store the data we need
    lithium_market_share_data = pd.DataFrame(index = minerals_market_share.index)
    
    # Get the lithium market share - this is going to be our target 
    lithium_market_share_data["lithium_market_share"] = minerals_market_share[["lithium"]]
    
    # Get the LFP market share 
    lfp_market_share = battery_yearly_market_shares[["lfp"]]
    
    # Convert the year index (currently an integer) to a datetime object
    lfp_market_share.index = pd.to_datetime(lfp_market_share.index, format = "%Y")
    
    # Extend the yearly market share data to be monthly 
    lfp_market_share_expanded = lfp_market_share.reindex(lithium_market_share_data.index, method = "ffill")
    
    # Add to the data 
    lithium_market_share_data["lfp_market_share"] = lfp_market_share_expanded
    
    # Add lithium spot prices to the data
    lithium_market_share_data["lithium_spot_prices"] = minerals_monthly_spot_prices[["lithium"]]
    
    return lithium_market_share_data

def model_lithium_market_share(lithium_market_share_data, metadata):
    
    # Get the X and y
    X = lithium_market_share_data[["lfp_market_share", "lithium_spot_prices"]]
    y = lithium_market_share_data[["lithium_market_share"]]
    
    # Normalize the features
    X_scaler = StandardScaler()
    X_scaled = X_scaler.fit_transform(X)
    
    # Get the scaled value of the predicted LFP market share
    lfp_market_share_value = 0.6
    lfp_market_share_scaled = X_scaler.transform([[lfp_market_share_value, 0]])[0][0]
    print(f"LFP Market Share of 0.6 scaled: {lfp_market_share_scaled}")
    
    # Normalize the target, just for graphing
    y_scaler = StandardScaler()
    y_scaled = y_scaler.fit_transform(y)
    
    # Convert X_scaled back to DataFrame to retain column names
    X_scaled = pd.DataFrame(X_scaled, columns = X.columns, index = X.index)
    y_scaled = pd.DataFrame(y_scaled, columns = y.columns, index = y.index)
    
    # Get the scaled value of the last known spot price of lithium
    last_lithium_spot_prices_scaled = X_scaled["lithium_spot_prices"].iloc[-1]
    print(f"Last known scaled spot price of lithium: {last_lithium_spot_prices_scaled}")
    
    plt.figure(figsize=(10, 6))
    for column in X_scaled.columns:
        plt.plot(lithium_market_share_data.index, X_scaled[column], label=f'{column}', linestyle='--')
    plt.plot(y.index, y_scaled, label = 'Target: Lithium Market Share (Scaled for graphing)', color = 'blue')
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.grid()
    plt.title('Features vs Target')
    plt.legend()
    #plt.show()
    
    # Linear Regression
    linear_reg = LinearRegression()
    linear_reg.fit(X_scaled, y)
    y_pred_lr = linear_reg.predict(X_scaled)
    r2_lr = r2_score(y, y_pred_lr)
    rmse_lr = np.sqrt(mean_squared_error(y, y_pred_lr))
    coefficients_lr = dict(zip(X.columns, linear_reg.coef_[0]))
    coefficients_lr['intercept'] = linear_reg.intercept_[0]

    # Decision Tree Regressor
    tree_reg = DecisionTreeRegressor(random_state=42)
    tree_reg.fit(X, y)
    y_pred_tr = tree_reg.predict(X)
    r2_tr = r2_score(y, y_pred_tr)
    rmse_tr = np.sqrt(mean_squared_error(y, y_pred_tr))
    coefficients_tr = dict(zip(X.columns, tree_reg.feature_importances_))

    # Create a dataframe to store results
    results = pd.DataFrame({
        'Model': ['Linear Regression', 'Decision Tree'],
        'R^2': [r2_lr, r2_tr],
        'RMSE': [rmse_lr, rmse_tr],
        'Coefficients': [coefficients_lr, coefficients_tr]
    }).set_index("Model")
    
    # Plotting the linear regression results
    plt.figure(figsize = (10, 6))
    plt.plot(y.index, y, label = 'Actual Values', color = 'blue')
    plt.plot(y.index, y_pred_lr, label='Predicted Values (Linear Regression)', color='red', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Lithium Market Share')
    plt.title('Linear Regression: Actual vs Predicted')
    plt.legend()
    plt.grid()
    #plt.show()
    
    return results

def get_linear_regression_parameters(results): 
    
    # Get the parameters from the Linear Regression 
    parameters = results.loc['Linear Regression', 'Coefficients']
    
    # Convert the parameters to a dataframe format 
    parameters = pd.DataFrame.from_dict(parameters, orient = "index", columns = ["Coefficients"])
    
    return parameters