from nicegui import ui
from frontend.product import get_product, get_charecteristics

def content(id) -> None:
    product = get_product(id)
    ui.page_title(product.name)
    characteristics = get_charecteristics(id)
    if product is not None:
        ui.button('Назад', on_click=lambda: ui.navigate.to('/')).props('outline').style('color: gray; border-color: gray;')
        # Display product details
        ui.html(f'''
        <strong>{product.name}</strong>
        <p>{product.article}</p>
        ''')
        
        ui.html(f'''
        <div class="row">
            <div class="col">
                <img src="{product.image}">
            </div>
            <div class="col">
                <h2>Характеристики</h2>
                <table>{characteristics.to_html(columns=['name', 'value'], index=False,header=False) if characteristics is not None else ''}</table>
            </div>
        </div>
        ''')
    else:
        # Display a "not found" message
        ui.markdown('# Product not found')