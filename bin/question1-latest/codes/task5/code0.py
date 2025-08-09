# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "scipy",
# ]
# ///
import pandas as pd
from scipy.stats import pearsonr

data = pd.read_csv('highest_grossing_films_processed.csv')
correlation, _ = pearsonr(data['Rank'], data['Peak'])

with open('q3_rank_peak_correlation.txt', 'w') as f:
    f.write(str(correlation))