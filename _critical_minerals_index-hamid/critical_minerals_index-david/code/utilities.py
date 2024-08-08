import pandas as pd
from typing import Dict, Tuple

def compress_metadata(
    display: Dict[str, bool], 
    folders: Dict[str, str],
    interpolation: Dict[str, bool]
    ) -> dict:
    
    # Put all the information in a dictionary 
    metadata = {
        "display": display, 
        "folders": folders
    }
    
    return metadata

def extract_metadata(
    metadata: dict
    ) -> Tuple[dict, dict]:
    
    # Extract the display metadata from the metadata dictionary
    display = metadata["display"]
    
    # Extract the folders meatdata from the metadata dictionary
    folders = metadata["folders"]
    
    return display, folders

def get_filepath(
    folder: str, 
    name: str, 
    extension = "csv"
    ) -> str: 
    
    # Convert all characters in name to lowercase 
    name = name.lower().replace(" ", "_")
    
    # Create the filepath string 
    filepath = f"{folder}/{name}.{extension}"
    
    return filepath

def download_results(data, output, name):
    data.to_csv(f"{output}/{name}.csv")