import base64

# read the data_uri from codes/task6/result6.txt by opening the file
with open("codes/task6/result6.txt", "r") as f:
    data_uri = f.read().strip()

# Step 1: Strip the prefix
header, encoded = data_uri.split(",", 1)  # "data:image/png;base64", "iVBOR..."

# Step 2: Decode base64
image_data = base64.b64decode(encoded)

# Step 3: Write to a file
with open("output.png", "wb") as f:
    f.write(image_data)