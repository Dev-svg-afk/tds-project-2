# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import pandas as pd

df = pd.read_csv('highest_grossing_films_processed.csv')
result = df[df['Gross'] >= 1.5e9].sort_values('Year').iloc[0]['Title']
with open('result_q2_film_name.txt', 'w') as f:
    f.write(result)