import pandas as pd
import os
import concurrent.futures
import gc
import logging

logging.basicConfig(level=logging.INFO)

lithium_keywords = ['lithium']
columns_to_keep = ['DATE', 'DocumentIdentifier', 'V2Themes', 'V2Tone']
checkpoint_dir = '/Volumes/T5EVO/gdelt_download/Lithium/checkpoints/'

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
    data_folder = f'/Volumes/T5EVO/gdelt_download/{year_folder}'
    output_file = f'/Volumes/T5EVO/gdelt_download/Lithium/Lithium_{year_folder}.csv'
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