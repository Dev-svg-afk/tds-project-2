# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "uvicorn",
#    "jsonschema"
# ]
# ///
import json

with open('total_sales.json', 'r') as file:
    data = json.load(file)

total_sales = data['total_sales']
tax_rate_percentage = 10
total_sales_tax = total_sales * (tax_rate_percentage / 100)

with open('total_sales_tax.json', 'w') as output_file:
    json.dump({'total_sales_tax': total_sales_tax}, output_file)