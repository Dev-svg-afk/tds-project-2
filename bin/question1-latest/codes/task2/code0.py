# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
# ]
# ///
import pandas as pd

data = pd.read_csv('highest_grossing_films_raw.csv')
data['Gross'] = data['Worldwide gross'].replace({'\$': '', ',': ''}, regex=True).str.extract('(\d+\.?\d*)')[0].astype(float)
data['Release Year'] = data['Year'].astype(int)
data['Rank'] = data['Rank'].astype(int)
data['Peak'] = data['Peak'].astype(int)
data = data[['Gross', 'Release Year', 'Rank', 'Peak']]
data.to_csv('highest_grossing_films_processed.csv', index=False)