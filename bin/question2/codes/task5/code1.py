# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "numpy",
#    "matplotlib",
#    "seaborn",
#    "fastparquet"
# ]
# ///
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

data = pd.read_parquet('court_33_10_delay_data.parquet')

plt.figure(figsize=(10, 6))
sns.scatterplot(data=data, x='year', y='days_delay')
sns.regplot(data=data, x='year', y='days_delay', scatter=False, color='red')

buffer = BytesIO()
plt.savefig(buffer, format='webp')
buffer.seek(0)
img_str = base64.b64encode(buffer.read()).decode('utf-8')
data_uri = f"data:image/webp;base64,{img_str}"

with open('delay_scatterplot_base64.txt', 'w') as f:
    f.write(data_uri)