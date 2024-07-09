# Advanced Dash Time Series Visualization with MongoDB and NLP

This repository contains a Dash application for visualizing time series data, generating word clouds, and performing natural language processing (NLP) tasks. The data is sourced from a MongoDB database, and the application includes additional features such as interactive data tables and text analysis.

## Files

- `app.py`: The main Dash application file.
- `preprocess_data.py`: The script for preprocessing raw data.

## Requirements

To run this project, you'll need to have the following Python packages installed:

- dash
- plotly
- pandas
- pymongo
- matplotlib
- wordcloud
- transformers
- nltk

## Steps
To run the dashboard in your local machine, run the preprocess.py first to do the data preprocessing. Then, run the app.py to display the dashboard. Remember to change your own Mongodb connection in both files.

You can install these packages using `pip`:

```sh
pip install dash plotly pandas pymongo matplotlib wordcloud transformers nltk
