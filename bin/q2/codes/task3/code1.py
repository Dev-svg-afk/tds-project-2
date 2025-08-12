# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "pyarrow",
# ]
# ///
import pandas as pd

input_file = 'filtered_judgments_metadata.parquet'
output_file_name = 'court_33_10_delay_data.parquet'

df = pd.read_parquet(input_file)
df['date_of_registration'] = pd.to_datetime(df['date_of_registration'], format='%d-%m-%Y')
df['decision_date'] = pd.to_datetime(df['decision_date'], format='%d-%m-%Y')
df_filtered = df[df['court'] == '33_10']
df_filtered['days_delay'] = (df_filtered['decision_date'] - df_filtered['date_of_registration']).dt.days
result = df_filtered[['year', 'days_delay']]
result.to_parquet(output_file_name)