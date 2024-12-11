from nicegui import ui
from frontend.product import get_product

def content(id) -> None:
    product = get_product(id)
    if product is None:
        ui.markdown('# Product not found')
        return
    
    ui.page_title(product.name)
    characteristics = product.characteristics
    chars_dict = {key:value for key, value in characteristics.items()}

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
            <table>{''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in chars_dict.items() if v is not None) if characteristics is not None else ''}</table>
        </div>
    </div>
    ''')