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
from io import BytesIO

data_file = 'prepared_sales_data.csv'
output_file_name = 'cumulative_sales_chart_base64.txt'

df = pd.read_csv(data_file)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df['Cumulative_Sales'] = df['Sales'].cumsum()

plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Cumulative_Sales'], color='red')
plt.title('Cumulative Sales Over Time')
plt.xlabel('Date')
plt.ylabel('Cumulative Sales')

buffer = BytesIO()
plt.savefig(buffer, format='png')
plt.close()
buffer.seek(0)

image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

if len(image_base64) < 100 * 1024:  # check file size under 100KB
    with open(output_file_name, 'w') as f:
        f.write(image_base64)