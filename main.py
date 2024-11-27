from frontend import *
from nicegui import app

app.add_static_files('/images', 'images')
app.add_static_files('/cache', 'cache')

def handle_shutdown():
    print('Shutdown has been initiated!')

app.on_shutdown(handle_shutdown)
ui.run()