# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "scikit-learn",
#    "fastparquet"
# ]
# ///
import pandas as pd
from sklearn.linear_model import LinearRegression

data = pd.read_parquet('court_33_10_delay_data.parquet')
X = data[['year']]
y = data['days_delay']

model = LinearRegression()
model.fit(X, y)
slope = model.coef_[0]

with open('regression_slope_delay.txt', 'w') as f:
    f.write(str(slope))