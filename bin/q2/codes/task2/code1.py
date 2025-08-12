# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "fastparquet"
# ]
# ///
import pandas as pd

df = pd.read_parquet('filtered_judgments_metadata.parquet')
filtered_df = df[df['year'].isin([2019, 2020, 2021, 2022])]
court_counts = filtered_df['court'].value_counts()
most_disposed_court = court_counts.idxmax()

with open('most_disposed_court.txt', 'w') as f:
    f.write(most_disposed_court)