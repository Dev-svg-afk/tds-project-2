# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "requests",
#   "beautifulsoup4",
# ]
# ///
import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
table = soup.find('table', class_='wikitable')
data = []

for row in table.find_all('tr')[1:]:
    cols = row.find_all(['td', 'th'])
    data.append([col.text.strip() for col in cols])

df = pd.DataFrame(data)
df.to_csv('result1.csv', index=False)

metadata = {
    'id': 1,
    'name': 'Scrape Data from Wikipedia',
    'description': 'Scrape the list of highest grossing films from the provided Wikipedia URL.',
    'url': url
}

pd.DataFrame([metadata]).to_json('metadata.json', orient='records', lines=False)