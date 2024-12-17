import json
import re
import requests
from config import AUDITBOARD_URL, AUDITABLE_ENTITIES, HEADERS_AUDITBOARD, SUPPLIER_ID_PATTERN

def get_auditboard_data(auditboard_vendors, auditboard_vendor_ids, file_path, ids_file_path):
    response = requests.get(AUDITBOARD_URL + AUDITABLE_ENTITIES + '?include=ownerUsers', headers=HEADERS_AUDITBOARD)
    if response.status_code != 200:
        print(response.status_code)
        exit(-1)
    data = response.json()

    for vendor in data['auditable_entities']:
        # matches = re.findall(SUPPLIER_ID_PATTERN, vendor['id_string'])
        # if matches:
        #     for id in matches:
        if vendor['id_string']:
            auditboard_vendors[vendor['uid']] = vendor
        auditboard_vendor_ids.append(f"{vendor['id_string']}, {vendor['id']}")

    with open(file_path, 'w') as file:
        json.dump(auditboard_vendors, file)

    with open(ids_file_path, 'w', encoding='utf-8') as file:
        for item in auditboard_vendor_ids:
            file.write(f'{item}\n')

    print(f'Processed {len(auditboard_vendors)} vendors as auditable entities')
    
    return auditboard_vendors

# Function to filter keys containing only digits
def filter_digit_keys(json_data):
    filtered_vendors = []
    for key in json_data.keys():
        if key.isdigit() and int(key) > 13000:
            filtered_vendors.append(json_data[key])
    return filtered_vendors


vendors = {}
vendor_ids = []
get_auditboard_data(vendors, vendor_ids, "./data/auditboard.json", "./data/auditboard_vendor_ids.txt")

# Read JSON data from a file into a variable called data
with open('./data/auditboard.json', 'r') as file:
    data = json.load(file)

# Get the list of keys that only contain digits
filtered_vendors = filter_digit_keys(data)

for vendor in filtered_vendors:
    vendor['uid'] = "SUP-" + vendor['uid']
    auditable_entity = { "auditable_entity": vendor }
    url = f"{AUDITBOARD_URL}{AUDITABLE_ENTITIES}/{vendor['id']}"
    with requests.put(url, json=auditable_entity, headers=HEADERS_AUDITBOARD) as response:
        print(f"Update for {vendor['id_string']}: {response.status_code}")