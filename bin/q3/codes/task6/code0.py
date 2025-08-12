# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
# ]
# ///
import pandas as pd
import json

data_file = 'prepared_sales_data.csv'
output_file_name = 'median_sales.json'

sales_data = pd.read_csv(data_file)
median_sales = sales_data['Sales'].median()

with open(output_file_name, 'w') as json_file:
    json.dump({'median_sales': median_sales}, json_file)