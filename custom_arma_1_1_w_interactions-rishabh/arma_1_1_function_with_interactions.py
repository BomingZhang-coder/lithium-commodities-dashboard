"""
Instructions: 

A genearl ARMA(p, q) model looks like this: 
r(t) = alpha0 + phi r(t-1) + e(t) - theta * e(t-1)
Such models are estimated by MLE (maximum likelihood), and are easy to estimate when e(0) is assumed zero.  The MLE procedure will then also produce AIC and BIC criteria which can be compared with the AR-models. 
Forecasting with such a model is not hard but does require some programming:
Expected[r(t)| time t-1 information] = mu + phi r(t-1) - theta e(t-1)
But what is e(t-1)? Well, if the process is invertible (theta < 1), the e(t-1) is a function of the whole path of r(t-tau, tau = 1, ..., t), and can be filled in recursively.  That is, 
e(t) = r(t) - alpha0 - phi * r(t-1) + theta e(t-1) and so starting at observation 1, you can get all the e(t)'s as a function of past r(t)'s. 

ARMA(1,1) with interactions looks like this: 
r(t) = alpha0 + [phi(1,0) + phi(1,1) * z(t-1,5)] * r(t-1) + e(t) - [theta(1,0) + theta(1,1) * z(t-1,5)] * e(t-1)  

Let
R = R(t)
R_1 = R(t-1)
Z_1 = z(t-1,5)

Rewritten, the model looks like: 
R = alpha0 + [phi(1,0) + phi(1,1) * Z_1] * R_1 + e(t) - [theta(1,0) + theta(1,1) * Z_1] * e(t-1)  
"""

def arma_1_1_interactions(R_1, Z_1):
    """
    Inputs: This function takes R_1, and Z_1 as inputs. These are listed under the "inputs" folder.
    
    Outputs: This function should output the following, preferably in a dictionary or a dataframe format: 
    1.  Adjusted R2 (R superscript 2 subscript adj)
    2.	AIC
    3.	BIC
    4.	Rho_1 (first autocorrelation of the residual)
    5.	Rho_2 (second autocorrelation of the residual)
    6.	Ljung Box Autocorrelation test on the residuals using three autocorrelations -report p-value. (It is Chi-square(3), and you can report the p-value). 
    7.  The coefficients alpha0, phi(1,0), phi(1,1), theta(1,0), theta(1,1)
    
    Hint(s): The .update() dictionary method allows a dictionary to be updated with the coefficient values 
    """