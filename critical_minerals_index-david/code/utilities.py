import pandas as pd

def download_results(data, output, name):
    data.to_csv(f"{output}/{name}.csv")