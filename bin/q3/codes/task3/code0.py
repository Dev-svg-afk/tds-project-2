# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
# ]
# ///
import pandas as pd
import json

data = pd.read_csv('prepared_sales_data.csv')
top_region = data.groupby('Region')['Sales'].sum().idxmax()

with open('top_region.json', 'w') as f:
    json.dump({'top_region': top_region}, f)