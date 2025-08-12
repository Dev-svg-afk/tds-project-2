# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
# ]
# ///
import pandas as pd

input_file_name = 'sample-sales.csv'
output_file_name = 'prepared_sales_data.csv'

df = pd.read_csv(input_file_name)
df['Sales'] = pd.to_numeric(df['sales'], errors='coerce')
df['Date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['Sales', 'region', 'Date'])
df.to_csv(output_file_name, index=False)