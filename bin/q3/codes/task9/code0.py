# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "uvicorn",
#    "httpx",
#    "fastapi"
# ]
# ///
import json

with open('total_sales.json') as f:
    total_sales = json.load(f)['total_sales']

with open('top_region.json') as f:
    top_region = json.load(f)['top_region']

with open('day_sales_correlation.json') as f:
    day_sales_correlation = json.load(f)['correlation']

with open('bar_chart_base64.txt', 'r', encoding='utf-8') as f:
    bar_chart = f.read().strip()

with open('median_sales.json') as f:
    median_sales = json.load(f)['median_sales']

with open('total_sales_tax.json') as f:
    total_sales_tax = json.load(f)['total_sales_tax']

with open('cumulative_sales_chart_base64.txt', 'r', encoding='utf-8') as f:
    cumulative_sales_chart = f.read().strip()

final_output = {
    'total_sales': total_sales,
    'top_region': top_region,
    'day_sales_correlation': day_sales_correlation,
    'bar_chart': bar_chart,
    'median_sales': median_sales,
    'total_sales_tax': total_sales_tax,
    'cumulative_sales_chart': cumulative_sales_chart
}

with open('final_analysis_results.json', 'w') as f:
    json.dump(final_output, f)