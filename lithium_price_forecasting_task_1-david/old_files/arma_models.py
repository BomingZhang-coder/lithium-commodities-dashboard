import pandas as pd 
from statsmodels.tsa.arima.model import ARIMA 
import matplotlib.pyplot as plt

data = pd.read_csv("lithium_carbonate_log_returns.csv")
log_returns = data["log_ret"]
log_returns.to_csv("log_returns.csv")

data["zero_dummy"] = (data["log_ret"] == 0).astype(int)

data["z(t, 5)"] = data["zero_dummy"].rolling(window = 5).sum()
data["z(t, 22)"] = data["zero_dummy"].rolling(window = 22).sum()
#data["z(t-1, 5)"] = data["zero_dummy"].rolling(window = 5)
data = data.dropna()

def arma_results(returns, p, q):
    arma = ARIMA(returns, order = (p, 0, q))
    results = arma.fit()
    return results.summary()

arma_results(log_returns, 1, 1) 

arma_results(log_returns, 1, 2)

#arma 
# model = ARIMA(log_returns, order = (1, 0, 1))
# results = model.fit() 

# print(results.summary())

# forecasts = results.get_forecast(steps = 5) 
# print(forecasts.summary_frame())

# # Plot residuals
# residuals = results.resid
# plt.figure(figsize=(10, 4))
# plt.plot(residuals)
# plt.title('Residuals from ARMA Model')
# plt.xlabel('Date')
# plt.ylabel('Residuals')
# plt.show()

import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Generate sample data (or use your own data)
np.random.seed(0)
n = 100  # number of data points
r = np.random.normal(size=n)
z = np.random.normal(size=n)

# Define the ARMA(1,1) model with interaction terms
def arma_interactions(params, r, z):
    alpha0 = params[0]
    phi_1_0 = params[1]
    phi_1_1 = params[2]
    theta_1_0 = params[3]
    theta_1_1 = params[4]
    
    n = len(r)
    e = np.zeros(n)
    r_hat = np.zeros(n)
    
    for t in range(1, n):
        interaction_z = z[t-1] * 5  # assuming z(t-1,5) means z(t-1) multiplied by 5
        r_hat[t] = (alpha0 +
                    (phi_1_0 + phi_1_1 * interaction_z) * r[t-1] -
                    (theta_1_0 + theta_1_1 * interaction_z) * e[t-1])
        e[t] = r[t] - r_hat[t]
        
    return e

# Define the objective function to minimize (sum of squared errors)
def objective_function(params, r, z):
    e = arma_interactions(params, r, z)
    return np.sum(e**2)

# Initial parameter guess
initial_params = [0, 0, 0, 0, 0]

# Optimize the parameters
result = minimize(objective_function, initial_params, args=(r, z), method='L-BFGS-B')

# Extract optimized parameters
alpha0, phi_1_0, phi_1_1, theta_1_0, theta_1_1 = result.x

# Print the results
print("Optimized Parameters:")
print(f"alpha0: {alpha0}")
print(f"phi(1,0): {phi_1_0}")
print(f"phi(1,1): {phi_1_1}")
print(f"theta(1,0): {theta_1_0}")
print(f"theta(1,1): {theta_1_1}")