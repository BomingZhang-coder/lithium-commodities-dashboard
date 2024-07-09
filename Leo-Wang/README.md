# Lithium-ion Battery Market Analysis Dashboard

This repository contains a Python script for generating a visual dashboard of the lithium-ion battery market. The dashboard includes various charts showing market shares, mineral usage by battery type, mineral prices, and a scaled index over time for different battery technologies.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before running the script, you will need to have Python installed along with the necessary libraries. The main libraries used in this project are Pandas, NumPy, and Plotly.

#### Install Python

Download and install Python from [python.org](https://www.python.org/downloads/).

#### Install Required Libraries

After installing Python, you need to install the required Python libraries. Run the following command to install them:

```bash
pip install pandas numpy plotly

## Code Description

This section explains the key components of the script for visualizing data related to lithium-ion batteries:

- **Data Preparation:**
  - `battery_types`: Specifies the types of batteries considered, such as LCO, LFP, NMC, NCA, and LMO.
  - `market_shares`: Random market shares for each battery type are generated using a Dirichlet distribution to ensure they sum to 100%.
  - `minerals`: Lists the minerals used in the batteries, including Lithium, Cobalt, Nickel, Manganese, and Iron.
  - `mineral_usage`: Random usage data for each mineral is generated and normalized so that the total for each battery type sums to 1.
  - `dates`: Creates a range of dates for one year, providing a time series aspect to the data.
  - `mineral_prices_ts`: Generates random price data for each mineral over the specified date range, simulating market price fluctuations.

- **Dataframes:**
  - `market_share_df`: A DataFrame that records the market share of each battery type, useful for analysis and visualization.
  - `mineral_usage_df`: A DataFrame detailing how much of each mineral each battery type uses, normalized to ensure consistency across types.

- **Calculation Function `calculate_index_over_time`:**
  - This function calculates an index for each date by weighing the mineral prices against their usage in each battery type. It reflects how the overall cost or impact of minerals in the battery industry changes over time based on market share and mineral usage.

- **Visualization:**
  - The script utilizes Plotly to create an interactive dashboard featuring:
    - A pie chart to display the global market share of different battery types.
    - Stacked bar charts to show the mineral usage by each battery type.
    - A bar chart of mineral prices for the latest date in the dataset.
    - Line charts to track the changes in the calculated index over time and the fluctuations in mineral prices across the year.
  - These visualizations help in interpreting complex data through graphical representations, making trends and relationships easier to understand.

## Visualization Output

The dashboard is designed to provide a comprehensive overview of the lithium-ion battery market, displaying critical metrics and trends that can impact business and manufacturing decisions. The interactivity offered by Plotly allows users to explore different facets of the data in detail.
