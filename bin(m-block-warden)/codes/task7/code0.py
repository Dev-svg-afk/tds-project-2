# requires-python = ">=3.11"
# dependencies = [
# ]
# ///
import json
import base64

with open('result_q1_count.txt', 'r') as f:
    count = f.read().strip()

with open('result_q4_plot_base64.txt', 'r') as f:
    image_base64 = f.read().strip()

with open('result_q3_correlation.txt', 'r') as f:
    correlation = f.read().strip()

with open('result_q4_film_name.txt', 'r') as f:
    film_name = f.read().strip()

result = [
    str(count),
    film_name,
    str(correlation),
    image_base64
]

with open('final_answers.json', 'w') as f: