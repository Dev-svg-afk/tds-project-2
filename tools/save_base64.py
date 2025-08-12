import base64

with open("cumulative_sales_chart_base64.txt", "r") as f:
    data_uri = f.read().strip()

# Step 1: Strip the prefix
# header, encoded = data_uri.split(",", 1)  # "data:image/png;base64", "iVBOR..."

# Step 2: Decode base64
image_data = base64.b64decode(data_uri)

# Step 3: Write to a file
with open("cumulative_sales_chart_base64.png", "wb") as f:
    f.write(image_data)