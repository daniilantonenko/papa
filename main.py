from frontend import router
from nicegui import app

app.add_static_files('/images', 'images')
app.add_static_files('/cache', 'cache')
app.add_static_files('/static', 'static')

def handle_shutdown():
    print('Shutdown has been initiated!')

app.on_shutdown(handle_shutdown)
router.ui.run(favicon="🚀")