import asyncio
from utils import load_json
from parser import *

async def main():
    # Load new data to database
    j = load_json('data.json')

    print('Saving data to database')
    await save_to_database(j)

    # Scan all Organizations
    print('Scanning all Organizations')
    await scan_all()

asyncio.run(main())
