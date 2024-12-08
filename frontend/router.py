from nicegui import ui
from frontend import admin_page, product_page, home_page, admin_catalog_page

@ui.page('/')
def home() -> None:
        home_page.content()
        
@ui.page('/admin')
def admin() -> None:
    admin_page.content()

@ui.page('/admin/catalog')
def admin_catalog() -> None:
    admin_catalog_page.content()

@ui.page('/product/{id}')
def product(id) -> None:
    product_page.content(id)