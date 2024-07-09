import pandas as pd
from pymongo import MongoClient
import os

# Define the keywords
up_key1 = ['lithium-ore', 'nickel', 'cobalt', 'lithium-future', 'lithium-mining-companies', 'nickel-futures',
           'spodumene', 'spodumenite', 'lithium-market-share', 'cobalt-oxide', 'nickel-index', 'lithium-ore-reserves',
           'lithium-etf', 'lithium-index', 'lithium-concentration', 'industry-grade', 'battery-grade', 'li2co3',
           'li-oh', 'lioh', 'lithium-mangnate', 'lithium-iron-phosphate', 'ternary-materials', 'lithium-refining',
           'lithium-carbonate', 'lithium-hydroxide', 'lithium-production']
up_key = up_key1
down_key1 = ['ev-car', 'electric-battery', 'lithium-battery', 'ev-car-subsidy', 'battery-subsidy', 'ev-company',
             'ev-sales', 'ev-tax-credit', 'battery-tax-credit', 'storage', 'lfp-battery', 'lithium-battery-companies',
             'price-of-li-ion-battery', 'ternary-lithium-battery']
down_key = down_key1

for space in ["+", "_", "%20"]:
    up_key2 = [sub.replace("-", space) for sub in up_key1]
    up_key = up_key + up_key2
    down_key2 = [sub.replace("-", space) for sub in down_key1]
    down_key = down_key + down_key2

up_key = list(set(up_key))
down_key = list(set(down_key))

def clean_column(df, column):
    df[column] = df[column].str.replace('[', '', regex=False)
    df[column] = df[column].str.replace(']', '', regex=False)
    df[column] = df[column].str.replace("'", '', regex=False)
    df[column] = df[column].str.replace('"', '', regex=False)
    return df

def clean_and_process_data(data):
    print("Cleaning and processing data")
    data['DATE'] = pd.to_datetime(data['DATE'], format='%Y%m%d%H%M%S')
    data = clean_column(data, 'FinalThemes')
    data['ActualThemes'] = data['FinalThemes'].str.split(',')
    data = data.explode('ActualThemes')
    data['ActualThemes'] = data['ActualThemes'].str.strip()

    # Filter data by keywords in DocumentIdentifier
    filtered_data = data[data['DocumentIdentifier'].str.contains('|'.join(up_key + down_key), case=False, na=False)]
    
    print(f"Filtered data shape: {filtered_data.shape}")
    return filtered_data

def preprocess_data():
    # Change the mongodb connection with your private account
    client = MongoClient('mongodb+srv://botongyuan00:Wojiaoybt1220@cluster0.okmf3dv.mongodb.net/')
    db = client.lithium
    processed_collection = db.cleaned_data

    # Set the folder path for your own use
    data_folder = '/Users/botongyuan/Desktop/raw-data'
    
    raw_data_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    for file in raw_data_files:
        print(f"Processing file: {file}")
        raw_data = pd.read_csv(os.path.join(data_folder, file))
        print(f"Raw data shape: {raw_data.shape}")
        cleaned_data = clean_and_process_data(raw_data)
        if not cleaned_data.empty:
            processed_collection.insert_many(cleaned_data.to_dict('records'))
            print(f"Inserted data for file: {file}")
        else:
            print(f"No data to insert for file: {file}")

if __name__ == '__main__':
    print("Starting data preprocessing...")
    preprocess_data()
    print("Data preprocessing completed.")
