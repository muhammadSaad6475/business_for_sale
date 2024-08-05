import json

# Path to your JSON file
file_path = 'business_for_sale_data20240803.json'

# Load JSON data from the file
with open(file_path, 'r') as file:
    data = json.load(file)

# Update the specified fields to an empty string
for item in data:
    item['businessListedBy'] = ""
    item['broker-phone'] = ""
    item['broker-name'] = ""

# Write the updated JSON data back to the file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("JSON data updated successfully.")