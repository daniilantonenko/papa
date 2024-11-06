from models import *
import pandas as pd
from nicegui import ui

# Define a function to get product data from your data store
def get_product(id):
    product = Product.get(id=id)

    return product

def get_charecteristics(product_id):
    characteristics = Product.get(Product.id == product_id).characteristics
    characteristics = pd.DataFrame(list(characteristics.dicts()))
    return characteristics

def get_quantity():
    quantity = Product.select().count()
    return quantity

def get_products():
    products = Product.select()
    products = pd.DataFrame(list(products.dicts()))
    return products

@ui.page('/')
def main_page():
    ui.page_title('Каталог')

    # Display product quantity
    quantity = get_quantity()
    ui.html(f'''
        <span>Всего в каталоге: {quantity} шт</span>
        ''')

    products = get_products()
    table = ui.table.from_pandas(products, row_key='id').props('grid')
    table.add_slot('item', r'''
        <q-card flat bordered :props="props" class="m-1 my-card">
            <q-card-section class="text-center">
                <strong>{{ props.row.name }}</strong>
            </q-card-section>
            <q-separator />
            <q-card-section class="text-center card-image">
                <a :href="'/product/' + props.row.id"><img :src="props.row.image ? props.row.image : require('./blank.png')"></a>
            </q-card-section>
        </q-card>
    ''')


    ui.add_css('''
        .my-card {
            width: 100%;
            max-width: 250px;
        }
        .card-image{
            overflow: hidden;
        }
    ''')


# Define a route for the product page
@ui.page('/product/{id}')
def product_page(id):
    product = get_product(id)
    ui.page_title(product.name)
    characteristics = get_charecteristics(id)
    if product is not None:
        ui.button('Назад', on_click=lambda: ui.navigate.to('/')).props('outline').style('color: gray; border-color: gray;')
        # Display product details
        ui.html(f'''
        <strong>{product.name}</strong>
        <p>{product.article}</p>
        <div class="row">
            <div class="col">
                <img src="{product.image}">
            </div>
            <div class="col">
                <h2>Характеристики</h2>
                <table>{ characteristics.to_html(columns=['name', 'value'], index=False,header=False) if characteristics is not None else ''}</table>
            </div>
        </div>
        ''')
    else:
        # Display a "not found" message
        ui.markdown('# Product not found')


        
ui.run(favicon="🚀")