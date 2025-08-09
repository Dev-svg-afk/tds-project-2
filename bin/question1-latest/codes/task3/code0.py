# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas"
# ]
# ///
import pandas as pd

data = pd.read_csv('highest_grossing_films_processed.csv')
count = data[(data['Gross'] >= 2000000000) & (data['Release Year'] < 2020)].shape[0]

with open('q1_2bn_movies_before_2020.txt', 'w') as f:
    f.write(str(count))