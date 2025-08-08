# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "matplotlib",
#   "scikit-learn",
#   "base64",
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64

data = pd.read_csv('highest_grossing_films_processed.csv')
x = data['Rank']
y = data['Peak']

plt.figure(figsize=(10, 6))
plt.scatter(x, y)
slope, intercept = np.polyfit(x, y, 1)
plt.plot(x, slope*x + intercept, color='red', linestyle='dotted')
plt.xlabel('Rank')
plt.ylabel('Peak')
plt.title('Rank vs Peak Scatterplot with Regression Line')

plt.savefig('temp_plot.png', format='png')
plt.close()

with open('temp_plot.png', 'rb') as img_file:
    encoded_string = base64.b64encode(img_file.read()).decode()
    
data_uri = f'data:image/png;base64,{encoded_string}'
if len(data_uri) < 100000:
    with open('result_q4_plot_base64.txt', 'w') as output_file:
        output_file.write(data_uri)