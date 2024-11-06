from frontend import *
from nicegui import app
from utils import load_json
from parser import save_to_database, scan_all

@app.get('/scan')
async def scan():
    await load_save_scan()

async def load_save_scan():
    # Load new data to database
    j = load_json('data.json')

    print('Saving data to database')
    await save_to_database(j)

    # Scan all Organizations
    print('Scanning all Organizations')
    await scan_all()

    print('Done!')

def handle_shutdown():
    print('Shutdown has been initiated!')

app.on_shutdown(handle_shutdown)
ui.run()