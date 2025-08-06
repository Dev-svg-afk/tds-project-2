import requests
import pandas as pd

url = 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'
tables = pd.read_html(url)
highest_grossing_films = tables[0]

with open('result.txt', 'w') as f:
    f.write(highest_grossing_films.to_string())