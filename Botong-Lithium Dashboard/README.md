The dashboard is testing locally right now and have not been deployed.

To run the dashboard in your local machine, run the preprocess.py first to do the data preprocessing. Then, run the app.py to display the dashboard. Remember to change your own Mongodb connection in both files.

# Dash Time Series Visualization

This repository contains a Dash application for visualizing time series data, along with a preprocessing script to prepare the data for visualization.

## Files

- `app.py`: The main Dash application file.
- `preprocess_data.py`: The script for preprocessing raw data.

## Requirements

To run this project, you'll need to have the following Python packages installed:

- dash
- dash-core-components
- dash-html-components
- plotly
- pandas

You can install these packages using `pip`:

```sh
pip install dash plotly pandas
