from utils import load_json
from parser import *
from nicegui import app, ui

@ui.page('/')
def main_page():
    ui.page_title('Catalog')
    ui.run(favicon="🚀")

    ui.button('Scan', on_click=scan)

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

