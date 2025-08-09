# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "pandas",
#    "requests",
#    "beautifulsoup4",
# ]
# ///
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', class_='wikitable')
data = []

for row in table.find_all('tr'):
    cols = row.find_all(['td', 'th'])
    cols = [col.get_text(strip=True) for col in cols]
    data.append(cols)

df = pd.DataFrame(data[1:], columns=data[0])
df.to_csv('highest_grossing_films_raw.csv', index=False)