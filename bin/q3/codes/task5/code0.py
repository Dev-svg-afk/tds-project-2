# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "matplotlib",
# ]
# ///
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io

df = pd.read_csv('prepared_sales_data.csv')
total_sales = df.groupby('region')['Sales'].sum()
plt.bar(total_sales.index, total_sales.values, color='blue')
plt.xlabel('Region')
plt.ylabel('Total Sales')
plt.title('Total Sales by Region')
plt.tight_layout()

buffer = io.BytesIO()
plt.savefig(buffer, format='png')
plt.close()
buffer.seek(0)
img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

with open('bar_chart_base64.txt', 'w') as f:
    f.write(img_str)