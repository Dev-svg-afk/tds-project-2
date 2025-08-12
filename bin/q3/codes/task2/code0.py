# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "json5"
# ]
# ///
import pandas as pd
import json

data = pd.read_csv('prepared_sales_data.csv')
total_sales = data['Sales'].sum()

with open('total_sales.json', 'w') as json_file:
    json.dump({'total_sales': total_sales}, json_file)