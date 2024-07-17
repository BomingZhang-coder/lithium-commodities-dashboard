import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.diagnostic as smd
from statsmodels.tsa.stattools import acf, q_stat
from scipy.optimize import least_squares
from utilities import convert_floats

# Function to replace 'k' with a custom value in dictionary keys only
def replace_k_in_keys(d, custom_value):
    return {key.replace('k', str(custom_value)): value for key, value in d.items()}

# Function to get the model 
def get_model_results(weekly_data, constants_dict, y):
    
    # Models dictionray containing the models 
    models = {}
    
    # Results dictionary containing diagnostics from the model
    results = {}
    
    # For every dataframe, run the model on it
    for day, data in weekly_data.items():
        
        # Get a copy of the weekly data
        modelling_data = data.copy()
        
        # Rename columns
        modelling_data.rename(columns = constants_dict, inplace = True)
        
        # Get the constants we need
        X = list(constants_dict.values())
        
        # Get the model
        model = sm.OLS(data[y], modelling_data[X]).fit()
        
        # Extract adjusted R-squared, AIC, and BIC
        adj_r2 = model.rsquared_adj
        aic = model.aic
        bic = model.bic

        # Calculate residuals
        residuals = model.resid

        # Calculate first and second autocorrelation of the residuals
        autocorrs = acf(residuals, nlags = 2, fft = False)
        rho_1 = autocorrs[1]
        rho_2 = autocorrs[2]

        # Ljung-Box test on residuals using three autocorrelations
        lb_test = smd.acorr_ljungbox(residuals, lags = [3], return_df = True)
        lb_pvalue = lb_test['lb_pvalue'].iloc[0]
        
        # Extract model coefficients
        coefficients = model.params.to_dict()
        
        # Store result
        result = {
            "Adjusted_R2": round(adj_r2, 6),
            "AIC": round(aic, 2),
            "BIC": round(bic, 2),
            "Rho_1": round(rho_1, 6),
            "Rho_2": round(rho_2, 6),
            "Ljung_Box_pvalue": round(lb_pvalue, 6)
        }
        
        # Update this dictionary with our parameters
        result.update(coefficients)
        
        results[day.capitalize()] = result
        models[day.capitalize()] = model
    
    return models, results

# Get the phi coefficient value from an AR(1) model
def get_phi(results):
    converted_results = convert_floats(results)
    results_df = pd.DataFrame.from_dict(converted_results, orient = "index")
    mean_phi_value = results_df["phi"].mean()
    return mean_phi_value

def fit_non_linear_ar1_model(weekly_data, phi_initial):

    # Define the logistic function
    def logistic_function(y):
        return np.exp(y) / (1 + np.exp(y))

    # Define the nonlinear AR(1) model
    def nonlinear_ar1_model(params, r, z_5):
        a, phi = params
        n = len(r)
        residuals = np.zeros(n)
        for t in range(1, n):
            x_t_minus_1 = 2 * logistic_function(a * z_5[t-1])
            residuals[t] = r[t] - (a + phi * x_t_minus_1 * r[t-1])
        return residuals

    # Define the residuals function for optimization
    def residuals(params, r, z_5):
        return nonlinear_ar1_model(params, r, z_5)
    
    # Initialising our results dictionary
    results = {}
    
    for day, data in weekly_data.items():
    
        # Convert DataFrame columns to numpy arrays
        r_values = data["r(t)"].values
        z_5_values = data["z(t,5)"].values

        # Initial parameter guesses
        initial_guess = [0, phi_initial]

        # Use least squares to fit the nonlinear model
        result = least_squares(residuals, initial_guess, args=(r_values, z_5_values))

        # Extract the estimated parameters
        a_est, phi_est = result.x
        coefficients = {
            "a": a_est, 
            "phi": phi_est
        }
        
        # Compute the residuals
        residuals_final = residuals(result.x, r_values, z_5_values)
        
        # Calculate the statistics
        n = len(r_values)
        k = 2  # Number of parameters (a and phi)
        ss_res = np.sum(residuals_final**2)
        ss_tot = np.sum((r_values - np.mean(r_values))**2)
        r2 = 1 - (ss_res / ss_tot)
        adj_r2 = 1 - (1 - r2) * ((n - 1) / (n - k - 1))
        aic = n * np.log(ss_res / n) + 2 * k
        bic = n * np.log(ss_res / n) + np.log(n) * k
        acf_vals = acf(residuals_final, fft=True, nlags=2)
        rho_1 = acf_vals[1]
        rho_2 = acf_vals[2]
        ljung_box_result = q_stat(acf_vals[1:4], n)
        lb_pvalue = ljung_box_result[1][-1]
        
        # Store result
        result = {
            "Adjusted_R2": round(adj_r2, 6),
            "AIC": round(aic, 2),
            "BIC": round(bic, 2),
            "Rho_1": round(rho_1, 6),
            "Rho_2": round(rho_2, 6),
            "Ljung_Box_pvalue": round(lb_pvalue, 6)
        }
        
        # Update this dictionary with our parameters
        result.update(coefficients)
        
        results[day.capitalize()] = result
    
    return results