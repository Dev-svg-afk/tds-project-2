# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///
import json

with open('q1_2bn_movies_before_2020.txt') as f:
    q1_result = json.load(f)
    answer_q1 = str(q1_result)

with open('q2_earliest_1_5bn_film_title.txt') as f:
    q2_result = json.load(f)
    answer_q2 = q2_result['preview']

with open('q3_rank_peak_correlation.txt') as f:
    q3_result = json.load(f)
    answer_q3 = str(float(q3_result['preview']))

with open('q4_scatterplot_image_data_uri.txt') as f:
    q4_result = json.load(f)
    answer_q4 = q4_result['preview']

final_answers = json.dumps([answer_q1, answer_q2, answer_q3, answer_q4])

with open('final_answers.json', 'w') as outfile:
    outfile.write(final_answers)