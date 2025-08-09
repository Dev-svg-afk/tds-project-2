# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "matplotlib",
#    "numpy",
# ]
# ///
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

df = pd.read_csv('highest_grossing_films_processed.csv')
x = df['Rank']
y = df['Peak']

plt.figure(figsize=(10, 6))
plt.scatter(x, y)
m, b = np.polyfit(x, y, 1)
plt.plot(x, m*x + b, color='red', linestyle='dotted')

plt.xlabel('Rank')
plt.ylabel('Peak')
plt.title('Scatterplot of Rank vs Peak with Regression Line')

buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
data_uri = f"data:image/png;base64,{image_base64}"

with open('q4_scatterplot_image_data_uri.txt', 'w') as f:
    f.write(data_uri[:100000])