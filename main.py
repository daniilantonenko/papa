import asyncio
from utils import load_json
from parser import *

async def main():
    # Load new data to database
    j = load_json('data.json')
    await save_to_database(j)

    # Scan all Organizations
    await scan_all()

asyncio.run(main())
