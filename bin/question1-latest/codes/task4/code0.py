# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
# ]
# ///
import pandas as pd

df = pd.read_csv('highest_grossing_films_processed.csv')
earliest_film = df[df['Gross'] > 1.5e9].sort_values('Release Year').iloc[0]
with open('q2_earliest_1_5bn_film_title.txt', 'w') as f:
    f.write(earliest_film['Title'])