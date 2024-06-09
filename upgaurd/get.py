import requests
import json
from collections import defaultdict
from config import UPGUARD_API_URL_BULK, HEADERS_UPGUARD, PAYLOAD
from utils.file_operations import print_info
import aiohttp
import asyncio

# def get_upguard_data(file_path):
#     print_info('Fetching upgaurd data...')
#     vendor_details = defaultdict(list)
#     vendor_count = 0
#     try:
#         while True:
#             response = requests.get(UPGUARD_API_URL_BULK, params=PAYLOAD, headers=HEADERS_UPGUARD, stream=True)
#             response_data = response.json()
#             vendor_count += len(response_data["vendors"])
#             print(f'retrieved {vendor_count} vendors')
#             for vendor in response_data['vendors']:
#                 supplier_id = vendor['attributes'].get('Supplier ID (Jaeggar & Workday)')
#                 vendor_details[supplier_id] = vendor
#             if 'next_page_token' in response_data:
#                 PAYLOAD['page_token'] = response_data['next_page_token']
#             else:
#                 break

#         with open(file_path, 'w') as json_file:
#             json.dump(vendor_details, json_file)
#     except requests.RequestException as e:
#         print(f"Request Exception: {e}")

async def fetch_vendor_data(session, page_token=None):
    payload = PAYLOAD.copy()
    if page_token:
        payload['page_token'] = page_token
    
    async with session.get(UPGUARD_API_URL_BULK, params=payload, headers=HEADERS_UPGUARD) as response:
        return await response.json()

async def get_all_vendors(file_path, concurrency_limit=100):
    print_info('Fetching upguard data...')
    vendor_details = defaultdict(list)
    vendor_count = 0

    timeout = aiohttp.ClientTimeout(
        total=500,        # Total timeout
        connect=500,       # Connection timeout
        sock_read=500,     # Socket read timeout
        sock_connect=500   # Socket connect timeout
    )

    async with aiohttp.ClientSession(timeout=timeout) as session:
        response_data = await fetch_vendor_data(session)
        total_results = response_data['total_results']
        vendor_count += len(response_data["vendors"])
        print(f'retrieved {vendor_count} vendors')
        
        for vendor in response_data['vendors']:
            supplier_id = vendor['attributes'].get('Supplier ID (Jaeggar & Workday)')
            vendor_details[supplier_id] = vendor

        tasks = []
        for offset in range(1000, total_results, 1000):
            tasks.append(fetch_vendor_data(session, page_token=str(offset)))
        
        responses = await asyncio.gather(*tasks)
        
        for response_data in responses:
            vendor_count += len(response_data["vendors"])
            print(f'retrieved {vendor_count} vendors')
            for vendor in response_data['vendors']:
                supplier_ids = vendor['attributes'].get('Supplier ID (Jaeggar & Workday)')
                if supplier_ids:
                    for id in supplier_ids.split(','):
                        vendor_details[id.strip()] = vendor
                
    with open(file_path, 'w') as json_file:
        json.dump(vendor_details, json_file)

