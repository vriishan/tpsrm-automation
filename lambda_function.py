import json
import time
import asyncio
from auditboard.get import get_auditboard_data, get_custom_field_options
from auditboard.users import get_auditboard_user_data
from upgaurd.get import get_all_vendors
from utils.file_operations import read_json, write_json
from upgaurd.update import run_upgaurd_update
from auditboard.update import run_auditboard_update
from config import AUDITBOARD_URL, AUDITABLE_ENTITIES, HEADERS_AUDITBOARD, SUPPLIER_ID_PATTERN
from mapping import field_mapping
import requests
import re
import os

# Initialize variables
auditboard_vendors = {}
auditboard_users = {}
auditboard_vendor_ids = []
upguard_file_path = './data/upgaurd.json'
auditboard_file_path = './data/auditboard.json'
auditboard_user_file_path = './data/users.json'

upgaurd_file = ""
auditboard_file = ""


def get_data():
    # Fetch data if files do not exist
    if not os.path.exists(upguard_file_path):
        start_time = time.time()
        upgaurd_file = asyncio.run(get_all_vendors(upguard_file_path))
        print(f"Upguard data retrieval time: {time.time() - start_time:.2f} seconds")

    if not os.path.exists(auditboard_file_path):
        start_time = time.time()
        auditboard_file = get_auditboard_data(auditboard_vendors, auditboard_vendor_ids, auditboard_file_path, './data/auditboard_vendor_ids.txt')
        print(f"Auditboard data retrieval time: {time.time() - start_time:.2f} seconds")

    if not os.path.exists(auditboard_user_file_path):
        start_time = time.time()
        auditboard_users = get_auditboard_user_data(auditboard_users, auditboard_user_file_path)
        print(f"Auditboard user data retrieval time: {time.time() - start_time:.2f} seconds")


def sync_auditboard_to_upgaurd():
    data = []
    # AUDITBOARD -> UPGAURD
    for supplier_id, auditboard_vendor in auditboard_file.items():
        if supplier_id in upguard_file and upguard_file[supplier_id]['primary_hostname']:
            payload_attributes = {}

            payload_attributes[field_mapping['upgaurd']['attributes']['TPSP Start Date']] = auditboard_vendor[field_mapping['auditboard']['TPSP Start Date']]
            
            payload_attributes[field_mapping['upgaurd']['attributes']['TPSP Completion Date']] = auditboard_vendor[field_mapping['auditboard']['TPSP Completion Date']]
            
            payload_attributes[field_mapping['upgaurd']['attributes']['TPSRA Start Date']] = auditboard_vendor[field_mapping['auditboard']['TPSRA Start Date']]
            
            payload_attributes[field_mapping['upgaurd']['attributes']['TPSRA Completion Date']] = auditboard_vendor[field_mapping['auditboard']['TPSRA Completion Date']]
            
            if len(auditboard_vendor[field_mapping['auditboard']['TPRO Name']]) > 0:
                owners = []
                for id in auditboard_vendor[field_mapping['auditboard']['TPRO Name']]:
                    owners.append(auditboard_users[str(id)]['full_name'])
                owners = ', '.join(owners)
                payload_attributes[field_mapping['upgaurd']['attributes']['TPRO Name']] = owners
            else:
                payload_attributes[field_mapping['upgaurd']['attributes']['TPRO Name']] = ""
            
            if 'field_data' in auditboard_vendor and field_mapping['auditboard']['TPSP Status'] in auditboard_vendor['field_data']:
                tpsp_status_id = auditboard_vendor['field_data'][field_mapping['auditboard']['TPSP Status']]
                status = auditboard_field_options[tpsp_status_id]['name']
                payload_attributes[field_mapping['upgaurd']['attributes']['TPSP Status']] = status
            else:
                payload_attributes[field_mapping['upgaurd']['attributes']['TPSP Status']] = ""
            
            if 'field_data' in auditboard_vendor and field_mapping['auditboard']['TPSRA Status'] in auditboard_vendor['field_data']:
                tpsra_status_id = auditboard_vendor['field_data'][field_mapping['auditboard']['TPSRA Status']]
                status = auditboard_field_options[tpsra_status_id]['name']
                payload_attributes[field_mapping['upgaurd']['attributes']['TPSRA Status']] = status
            else:
                payload_attributes[field_mapping['upgaurd']['attributes']['TPSRA Status']] = ""

            payload = {
                "attributes": payload_attributes,
                "vendor_primary_hostname": upguard_file[supplier_id]['primary_hostname']
            }

            data.append(payload)

    asyncio.run(run_upgaurd_update(data))
    print(f'Updated {len(data)} vendors on Upguard')


def sync_upgaurd_to_auditboard():
    # UPGAURD -> AUDITBOARD
    i = 0
    data = []
    for supplier_id, auditboard_vendor in auditboard_file.items():
        if supplier_id in upguard_file:
            auditable_entity = {}
            auditable_entity['id'] = auditboard_vendor['id']
            auditable_entity['id_string'] = auditboard_vendor['id_string']

            # sync score
            if field_mapping['upgaurd']['upgaurdScore'] in upguard_file[supplier_id]:
                auditable_entity[field_mapping['auditboard']['upgaurdScore']] = upguard_file[supplier_id][field_mapping['upgaurd']['upgaurdScore']]
        
            # sync vendor URL
            if field_mapping['upgaurd']['vendorURL'] in upguard_file[supplier_id]:
                auditable_entity[field_mapping['auditboard']['vendorURL']] = upguard_file[supplier_id][field_mapping['upgaurd']['vendorURL']]

            payload = {"auditable_entity": auditable_entity}
            i += 1
            data.append(payload)

    asyncio.run(run_auditboard_update(data))
    print(f'Updated {i} Auditboard vendors')


# Read data from files
# upguard_file = read_json(upguard_file_path)
# auditboard_file = read_json(auditboard_file_path)
# auditboard_users = read_json(auditboard_user_file_path)

auditboard_custom_fields = get_custom_field_options()
auditboard_field_options = {}

for option in auditboard_custom_fields['custom_field_options']:
    auditboard_field_options[option['id']] = option


def display_menu_for_input():
    menu_options = {
        1: "-------------------------------------------------",
        2: "Find vendors on Auditboard without a supplier ID",
        3: "Sync Auditboard data (TPSP/TPSRA status and dates, TPRO owners) to Upgaurd",
        4: "Sync Vendor URL, Upgaurd scores to Auditboard",
        5: "Exit"
    }

    print("Select an option:")
    for key, value in menu_options.items():
        print(f" {key}. {value}")

    choice = input("Enter your choice here: ")
    return choice

# Interactive menu
# while True:
#     choice = display_menu_for_input()

#     if choice == '1':
#         pass

#     elif choice == '2':
#         try:
#             response = requests.get(AUDITBOARD_URL + AUDITABLE_ENTITIES, headers=HEADERS_AUDITBOARD)
#             data = response.json()

#             count = 0
#             for vendor in data['auditable_entities']:
#                 if not re.search(SUPPLIER_ID_PATTERN, vendor['id_string']):
#                     auditboard_vendors[vendor['id']] = vendor
#                     count += 1

#             write_json(auditboard_vendors, './data/auditboardDataNoSupplierId.json')
#             print(f'Processed {count} vendors without supplier IDs')
#         except requests.RequestException as e:
#             print(f"Request Exception: {e}")

#     elif choice == '3':
#         sync_auditboard_to_upgaurd()

#     elif choice == '4':
#         sync_upgaurd_to_auditboard()

#     elif choice == '5':
#         break

#     else:
#         print("Invalid option, please try again.")


def lambda_handler(event, context):
    get_data()
    sync_auditboard_to_upgaurd()
    sync_upgaurd_to_auditboard()
    return {
        'statusCode': 200,
        'body': json.dumps('Automation sync ran successfully')
    }
