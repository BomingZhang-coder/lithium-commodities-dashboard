import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from math import log
import matplotlib.pyplot as plt

def get_modelling_data(
    minerals_market_share: pd.DataFrame, 
    battery_yearly_market_shares: pd.DataFrame, 
    minerals_monthly_spot_prices: pd.DataFrame,
    exchange_rates: pd.DataFrame, 
    inflation_consumer_prices: pd.DataFrame,
    google_trends_lithium: pd.DataFrame, 
    metadata
) -> pd.DataFrame: 
    
    # Create a DataFrame to store the data we need
    modelling_data = pd.DataFrame(index = minerals_market_share.index)
    
    # Get the lithium market share - this is going to be our target 
    modelling_data["lithium_market_share"] = minerals_market_share[["lithium"]]
    
    # Get the LFP market share 
    lfp_market_share = battery_yearly_market_shares[["lfp"]]
    
    # Convert the year index (currently an integer) to a datetime object
    lfp_market_share.index = pd.to_datetime(lfp_market_share.index, format = "%Y")
    
    # Extend the yearly market share data to be monthly 
    lfp_market_share_expanded = lfp_market_share.reindex(modelling_data.index, method = "ffill")
    
    # Add to the data 
    modelling_data["lfp_market_share"] = lfp_market_share_expanded

    # Add lithium spot prices to the data
    modelling_data["lithium_spot_prices"] = minerals_monthly_spot_prices[["lithium"]]

    for column in exchange_rates.columns: 
        modelling_data[column] = exchange_rates[[column]]

    for column in inflation_consumer_prices.columns: 
        modelling_data[column] = inflation_consumer_prices[[column]]
    
    google_trends_column = google_trends_lithium.columns[0]
    modelling_data[google_trends_column] = google_trends_lithium[[google_trends_column]]

    modelling_data.dropna(inplace = True)

    modelling_data.to_csv("results/modelling_data.csv")

    return modelling_data

def model_lithium_market_share(data, metadata):
    # Function to perform the analysis
    def perform_analysis(data, include_google_trends):
        if not include_google_trends:
            data = data.drop(columns=['google_trends_interest'])
            
        # Normalize the data (z-score normalization)
        scaler = StandardScaler()
        data_scaled = pd.DataFrame(scaler.fit_transform(data.drop(columns=['lithium_market_share'])), columns=data.columns[1:], index=data.index)
        data_scaled['lithium_market_share'] = data['lithium_market_share'].values

        # Parameters for rolling window
        window_size = 12
        n_predictions = len(data) - window_size

        # Initialize lists to store results
        results = {
            'linear_regression': {'predictions': [], 'actuals': [], 'dates': []},
            'decision_tree': {'predictions': [], 'actuals': [], 'dates': []}
        }

        # Store the last fitted models for extracting coefficients and feature importances
        last_lin_reg = None
        last_tree = None

        # Rolling window evaluation
        for start in range(n_predictions):
            end = start + window_size
            train_data = data_scaled.iloc[start:end]
            test_data = data_scaled.iloc[end:end+1]

            X_train = train_data.drop(columns=['lithium_market_share'])
            y_train = train_data['lithium_market_share']
            X_test = test_data.drop(columns=['lithium_market_share'])
            y_test = test_data['lithium_market_share'].values
            test_date = data.index[end:end+1].values[0]

            # Linear Regression
            lin_reg = LinearRegression()
            lin_reg.fit(X_train, y_train)
            y_pred_lin = lin_reg.predict(X_test)
            
            # Replace negative predictions with NaN
            y_pred_lin = [pred if pred >= 0 else np.nan for pred in y_pred_lin]
            
            results['linear_regression']['predictions'].extend(y_pred_lin)
            results['linear_regression']['actuals'].extend(y_test)
            results['linear_regression']['dates'].extend([test_date])
            last_lin_reg = lin_reg  # Store the last fitted linear regression model
            
            # Decision Tree
            tree = DecisionTreeRegressor()
            tree.fit(X_train, y_train)
            y_pred_tree = tree.predict(X_test)
            
            # Replace negative predictions with NaN
            y_pred_tree = [pred if pred >= 0 else np.nan for pred in y_pred_tree]
            
            results['decision_tree']['predictions'].extend(y_pred_tree)
            results['decision_tree']['actuals'].extend(y_test)
            results['decision_tree']['dates'].extend([test_date])
            last_tree = tree  # Store the last fitted decision tree model

        # Calculate metrics
        def calculate_metrics(actuals, predictions, k):
            valid_indices = [i for i in range(len(predictions)) if not np.isnan(predictions[i])]
            valid_actuals = [actuals[i] for i in valid_indices]
            valid_predictions = [predictions[i] for i in valid_indices]
            
            if len(valid_actuals) == 0 or len(valid_predictions) == 0:
                return np.nan, np.nan, np.nan, np.nan
            
            mse = mean_squared_error(valid_actuals, valid_predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(valid_actuals, valid_predictions)
            n = len(valid_actuals)
            aic = n * log(mse) + 2 * k
            bic = n * log(mse) + k * log(n)
            return rmse, r2, aic, bic

        k = X_train.shape[1]  # number of predictors

        lin_metrics = calculate_metrics(results['linear_regression']['actuals'], results['linear_regression']['predictions'], k)
        tree_metrics = calculate_metrics(results['decision_tree']['actuals'], results['decision_tree']['predictions'], k)

        average_metrics = pd.DataFrame({
            'Linear Regression': lin_metrics,
            'Decision Tree': tree_metrics
        }, index=['RMSE', 'Adjusted R2', 'AIC', 'BIC'])

        # Extract coefficients from the linear regression model
        coefficients = pd.DataFrame({
            'Feature': X_train.columns,
            'Linear Regression Coefficients': last_lin_reg.coef_
        })

        # Extract feature importances from the decision tree model
        feature_importances = pd.DataFrame({
            'Feature': X_train.columns,
            'Decision Tree Importances': last_tree.feature_importances_
        })

        # Combine both into a single DataFrame for display
        importance_df = pd.merge(coefficients, feature_importances, on='Feature')

        return average_metrics, importance_df, results

    # Perform analysis including google_trends_interest
    metrics_incl, importance_incl, results_incl = perform_analysis(data, include_google_trends=True)

    # Perform analysis excluding google_trends_interest
    metrics_excl, importance_excl, results_excl = perform_analysis(data, include_google_trends=False)

    print("\nAverage Metrics Including Google Trends Interest:")
    print(metrics_incl)
    print("\nCoefficients and Feature Importances Including Google Trends Interest:")
    print(importance_incl)

    print("\nAverage Metrics Excluding Google Trends Interest:")
    print(metrics_excl)
    print("\nCoefficients and Feature Importances Excluding Google Trends Interest")
    print(importance_excl)

    # Plotting the results
    def plot_results(results, title):
        plt.figure(figsize=(12, 6))
        plt.plot(results['linear_regression']['dates'], results['linear_regression']['actuals'], label='Actual Values', marker='o')
        plt.plot(results['linear_regression']['dates'], results['linear_regression']['predictions'], label='Linear Regression Predictions', marker='x')
        plt.plot(results['linear_regression']['dates'], results['decision_tree']['predictions'], label='Decision Tree Predictions', marker='s')
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Lithium Market Share')
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()

    # Plot results including google_trends_interest
    plot_results(results_incl, 'Predictions vs Actuals Including Google Trends Interest')

    # Plot results excluding google_trends_interest
    plot_results(results_excl, 'Predictions vs Actuals Excluding Google Trends Interest')