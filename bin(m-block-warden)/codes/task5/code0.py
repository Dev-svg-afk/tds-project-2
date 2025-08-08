# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "numpy",
# ]
# ///
import pandas as pd
import numpy as np

df = pd.read_csv('highest_grossing_films_processed.csv')
correlation = df['Rank'].corr(df['Peak'])
with open('result_q3_correlation.txt', 'w') as f:
    f.write(str(float(correlation)))