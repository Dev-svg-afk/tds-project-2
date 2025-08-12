# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "scipy",
# ]
# ///
import pandas as pd
import json
from scipy.stats import pearsonr

data = pd.read_csv('prepared_sales_data.csv')
data['Date'] = pd.to_datetime(data['Date'])
data['day_of_month'] = data['Date'].dt.day
correlation_coefficient, _ = pearsonr(data['day_of_month'], data['Sales'])

result = {'correlation': correlation_coefficient}
with open('day_sales_correlation.json', 'w') as output_file:
    json.dump(result, output_file)