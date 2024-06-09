import requests
import aiohttp
import asyncio
from config import UPGUARD_URL_BASE, VENDOR_ATTRIBUTES, HEADERS_UPGUARD

def update_vendor_entity(vendor_entity, data):
    response = requests.put(UPGUARD_URL_BASE + VENDOR_ATTRIBUTES, json=data, headers=HEADERS_UPGUARD)
    if response.status_code == 200:
        print(f"Update for {vendor_entity['Supplier ID (Jaeggar & Workday)']} successful")
    else:
        print(f"Update for {vendor_entity['Supplier ID (Jaeggar & Workday)']} returned {response.status_code}")

async def update_upguard_vendor(session, data, semaphore):
    async with semaphore:
        try:
            async with session.put(UPGUARD_URL_BASE + VENDOR_ATTRIBUTES, json=data, headers=HEADERS_UPGUARD) as response:
                print(f"{data['vendor_primary_hostname']}: {response.status}")
                # do something with response (success only) if necessary
                # return await response.json()
        except aiohttp.client_exceptions.ServerDisconnectedError:
            print(f"ServerDisconnected error updating {data['vendor_primary_hostname']}")
        except aiohttp.client_exceptions.ClientOSError:
            print(f"ClientOS/No network error updating {data['vendor_primary_hostname']}")

async def run_upgaurd_update(data):
    tasks = []
    concurrency = 150
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        for d in data:
            tasks.append(asyncio.create_task(update_upguard_vendor(session, d, semaphore)))
        await asyncio.gather(*tasks)
