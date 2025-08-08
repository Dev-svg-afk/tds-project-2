# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import pandas as pd

df = pd.read_csv('highest_grossing_films_processed.csv')
count = len(df[(df['gross_revenue'] >= 2000000000) & (df['release_year'] < 2020)])
with open('result_q1_count.txt', 'w') as f:
    f.write(str(count))