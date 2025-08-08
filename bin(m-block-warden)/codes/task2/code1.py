# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import pandas as pd

df = pd.read_csv('highest_grossing_films_raw.csv')
df['Worldwide gross'] = df['Worldwide gross'].replace({'\$': '', ',': ''}, regex=True)
df['Worldwide gross'] = pd.to_numeric(df['Worldwide gross'], errors='coerce')
df['Peak'] = df['Peak'].astype(int)
df['Rank'] = df['Rank'].astype(int)
df['Year'] = df['Year'].astype(int)
df.to_csv('highest_grossing_films_processed.csv', index=False)