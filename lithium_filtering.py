import pandas as pd
import os
import concurrent.futures
import gc
import logging
from itertools import product

logging.basicConfig(level=logging.INFO)

def generate_url_combinations(keywords_raw_list):
    # Initialize the output list
    keywords = []
    
    for keyword in keywords_raw_list:
    
         # Initialize a list for all possible combinations if there is a space in the keyword
         url_combinations = []
    
         # Check if the input string contains spaces
         if ' ' in keyword:
             # Define the separators we want to use
             separators = ['+', '_', '%20', '-', '']
        
             # Split the input string into words
             words = keyword.lower().split()
        
             # Generate all combinations of separators between words
             all_combinations = list(product(separators, repeat=len(words) - 1))
        
             # Create the final list of URL combinations
             for combination in all_combinations:
                 url = words[0]
                 for word, separator in zip(words[1:], combination):
                     url += separator + word
                 url_combinations.append(url)
         else:
             # If there are no spaces, append the original string in lowercase
             url_combinations.append(keyword.lower())
         
         keywords += url_combinations

    return keywords

lithium_keywords = generate_url_combinations([
     # Critical Minerals
     'lithium',
     'copper',
     'cobalt',
     'manganese',
     'nickel',
     'graphite',

     # Battery-related 
     'battery',
     'batterie',

     'lfp',
     'nmc',
     'nca',

     # Biggest Lithium-ion Manufacturers
     'catl',
     'contemporary amperex technology',
     'lg energy',
     'lg chem',
     'panasonic',
     'samsung',
     'svolt',
     'lishen',
     'eve energy',

     # Mining-related 
     'mine explosion',
     'mining explosion',

     'mine disaster',
     'mining disaster',

     'mine accident',
     'mining accident',

     'mine fatality',
     'mine fatalities',
     'mining fatality',
     'mining fatalities',

     'mine collapse',
     'mining collapse',

     'mine safety',
     'mining safety',

     'mine fire',
     'mining fire',

     'mine flood',
     'mining flood',

     'mine incident',
     'mining incident',

     'mine spill',
     'mining spill',

     'mine environment',
     'mining environment',

     'mine pollute',
     'mine pollution',
     'mining pollute',
     'mining pollution',

     'mining investment',
     'mine investment',

     'mineral prospect',
     'mine prospect', 
     'mining prospect',

     'mine regulation',
     'mining regulation',

     # Lithium Mining Companies
     'jiangxi special electric motor',

     'ganfeng',

     'sichuan yahua',

     'albemarle corporation',
     'albemarle corp',
     'albemarle mining',
     'albemarle mine',

     'eramet',

     'mineral resources', 

     'pilbara minerals',

     'sociedad química y minera',
     'sociedad quimica y minera',
     'sociedad qu mica y minera',
     'SQM',

     'sayona',

     'wealth minerals',

     'arcadium',
     'allkem',
     'livent',
     'orocobre',
     'galaxy resources',

     'rio tinto',

     'nmdc limited',
     'nmdc ltd',
     'national mineral development corporation', 
     'national mineral development corp',

     'medaro mining',
     'medaro mine', 

     'zijin mining',
     'zijin mine',

     # Macroeconomic Factors and Geopolitical Factors
     'us economy',
     'u s economy',
     'us economic',
     'u s economic',

     'china economy',
     'chinas economy',
     'china economic',
     'chinas economic', 

     'us inflation',
     'u s inflation',

     'china inflation', 
     'chinas inflation',
     
     'trade war',
     'trade agreement',

     # EV-related queries
     'ev sales',
     'ev market',
     'ev adoption',
     'ev demand',
     'ev cost',
     'ev price',
     'ev maker',
     'ev automaker',
     'ev manufacturer',

     'ev charger',
     'ev charging', 
     'ev supercharger',
     'ev supercharging',

     'ev tax',
     'ev rebate',
     'ev credit',

     'ev policy',
     'ev policies',
     'ev regulation', 
     'ev regulations',

     # Biggest players in the EV market
     'byd', 
     'tesla', 
     'volkswagen',
     'general motors',
     'stellantis',
     'bmw',
     'hyundai',
     'mercedes benz',
     'geely',
     'gac motor',
     'changan',
])

# print(lithium_keywords)
# quit()

columns_to_keep = ['DATE', 'DocumentIdentifier', 'V2Themes', 'V2Tone']
checkpoint_dir = '/opt/render/project/src/checkpoints/'
os.makedirs(checkpoint_dir, exist_ok=True)

os.makedirs(checkpoint_dir, exist_ok=True)

def clean_and_process_data(file):
    try:
        logging.info(f"Cleaning and processing file: {file}")
        data = pd.read_csv(file)
        data['DATE'] = pd.to_datetime(data['DATE'], format='%Y%m%d%H%M%S', errors='coerce')

        filtered_data = data[
            data['DocumentIdentifier'].str.contains('|'.join(lithium_keywords), case=False, na=False)
        ]

        filtered_data = filtered_data[columns_to_keep]
        logging.info(f"Filtered data shape for {file}: {filtered_data.shape}")
        return filtered_data
    except Exception as e:
        logging.error(f"Error processing file {file}: {e}")
        return pd.DataFrame()

def preprocess_data_for_year(year_folder):
    data_folder = f'/opt/render/project/src/{year_folder}'
    output_file = f'/opt/render/project/src/filtered_news_{year_folder}.csv'
    processed_files_log = f'{checkpoint_dir}processed_files_{year_folder}.txt'


    if os.path.exists(processed_files_log):
        with open(processed_files_log, 'r') as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()

    raw_data_files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith('.csv')]
    raw_data_files = [f for f in raw_data_files if f not in processed_files]

    all_cleaned_data = []
    batch_size = 15

    for i in range(0, len(raw_data_files), batch_size):
        batch_files = raw_data_files[i:i + batch_size]
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(clean_and_process_data, batch_files))

        for result, file in zip(results, batch_files):
            if not result.empty:
                all_cleaned_data.append(result)
                logging.info(f"Added cleaned data from processed file: {file}")
                with open(processed_files_log, 'a') as f:
                    f.write(f"{file}\n")
            else:
                logging.info(f"No data to add from processed file: {file}")

        gc.collect()

    if all_cleaned_data:
        final_cleaned_data = pd.concat(all_cleaned_data, ignore_index=True)
        final_cleaned_data.to_csv(output_file, index=False)
        logging.info(f"Saved aggregated cleaned data to file: {output_file}")
    else:
        logging.info("No data to save.")

def preprocess_all_years():
    year_folders = ['2018', '2019', '2020', '2021', '2022', '2023']
    for year_folder in year_folders:
        logging.info(f"Processing data for year: {year_folder}")
        preprocess_data_for_year(year_folder)
        logging.info(f"Completed processing for year: {year_folder}")

if __name__ == '__main__':
    logging.info("Starting data preprocessing for all years...")
    preprocess_all_years()
    logging.info("Data preprocessing for all years completed.")