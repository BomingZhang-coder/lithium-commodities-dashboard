import pandas as pd
from sklearn.preprocessing import StandardScaler

def z_score_normalise(df):
    # Initialize the StandardScaler
    scaler = StandardScaler()

    # Fit and transform the data
    scaled_data = scaler.fit_transform(df)

    # Convert the scaled data back to a DataFrame
    df_scaled = pd.DataFrame(scaled_data, columns=df.columns)
    
    return df_scaled