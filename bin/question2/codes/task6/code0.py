# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///
import json

with open('most_disposed_court.txt', 'r', encoding='utf-8') as file:
    most_disposed_court = file.read().strip()

with open('regression_slope_delay.txt', 'r', encoding='utf-8') as file:
    regression_slope_delay = file.read().strip()

with open('delay_scatterplot_base64.txt', 'r', encoding='utf-8') as file:
    delay_scatterplot_base64 = file.read().strip()

final_answers = {
    "What is the most disposed court?": most_disposed_court,
    "What is the regression slope for delay?": regression_slope_delay,
    "What is the base64 encoded scatterplot of delay?": delay_scatterplot_base64
}

with open('final_answers.json', 'w', encoding='utf-8') as output_file:
    json.dump(final_answers, output_file, ensure_ascii=False, indent=2)