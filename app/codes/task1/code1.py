# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "requests",
#    "pandas",
#    "beautifulsoup4",
# ]
# ///
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

url = 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', class_='wikitable')
df = pd.read_html(StringIO(str(table)))[0]
df.to_csv('highest_grossing_films_raw.csv', index=False)