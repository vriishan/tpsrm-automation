import requests
import re
import json
from config import AUDITBOARD_URL, USERS, HEADERS_AUDITBOARD, SUPPLIER_ID_PATTERN
from utils.file_operations import print_info

def get_auditboard_user_data(auditboard_users, file_path):
    print_info('Fetching auditboard user data...')
    response = requests.get(AUDITBOARD_URL + USERS, headers=HEADERS_AUDITBOARD)
    data = response.json()

    for user in data['users']:
        auditboard_users[user['id']] = user
        
    with open(file_path, 'w') as file:
        json.dump(auditboard_users, file)

    print(f"Processed {len(data['users'])} users as auditbord users")

    return auditboard_users
