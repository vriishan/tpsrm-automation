import requests
from config import AUDITBOARD_URL, AUDITABLE_ENTITIES, HEADERS_AUDITBOARD
import asyncio
import aiohttp

async def update_auditable_entity(session, auditable_entity, semaphore):
    async with semaphore:
        entity=auditable_entity['auditable_entity']
        url = f"{AUDITBOARD_URL}{AUDITABLE_ENTITIES}/{entity['id']}"
        async with session.put(url, json=auditable_entity, headers=HEADERS_AUDITBOARD) as response:
            print(f"Update for {entity['id_string']}: {response.status}")

async def run_auditboard_update(data, concurrency_limit=100):
    semaphore = asyncio.Semaphore(concurrency_limit)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for auditable_entity in data:
            task = update_auditable_entity(session, auditable_entity, semaphore)
            tasks.append(task)
        await asyncio.gather(*tasks)
        