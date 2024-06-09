import requests
import re
import json
from config import AUDITBOARD_URL, AUDITABLE_ENTITIES, AUDITBOARD_CUSTOM_FIELDS, HEADERS_AUDITBOARD, SUPPLIER_ID_PATTERN
from utils.file_operations import print_info

def get_auditboard_data(auditboard_vendors, auditboard_vendor_ids, file_path, ids_file_path):
    print_info('Fetching auditboard data...')
    response = requests.get(AUDITBOARD_URL + AUDITABLE_ENTITIES + '?include=ownerUsers', headers=HEADERS_AUDITBOARD)
    if response.status_code != 200:
        print(response.status_code)
        exit(-1)
    data = response.json()

    for vendor in data['auditable_entities']:
        matches = re.findall(SUPPLIER_ID_PATTERN, vendor['id_string'])
        if matches:
            for id in matches:
                auditboard_vendors[id] = vendor
        auditboard_vendor_ids.append(f"{vendor['id_string']}, {vendor['id']}")

    with open(file_path, 'w') as file:
        json.dump(auditboard_vendors, file)

    with open(ids_file_path, 'w', encoding='utf-8') as file:
        for item in auditboard_vendor_ids:
            file.write(f'{item}\n')

    print(f'Processed {len(auditboard_vendors)} vendors as auditable entities')

def get_auditboard_entity(entity_id):
    response = requests.get(AUDITBOARD_URL + AUDITABLE_ENTITIES + '/' + entity_id, headers=HEADERS_AUDITBOARD)
    data = response.json()
    return data['auditable_entities'][0]

def get_custom_field_options():
    payload = {"include": "fieldable,customFieldModels,customFieldOptions"}
    response = requests.post(AUDITBOARD_URL + AUDITBOARD_CUSTOM_FIELDS, data=payload, headers=HEADERS_AUDITBOARD)
    data = response.json()

    with open('./data/field-options.json', 'w') as file:
        json.dump(data, file)
    
    return data
    

