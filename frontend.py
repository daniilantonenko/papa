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

class PageExpansion:
    def __init__(self, container) -> None:
        self.container = container
    
    def add(self, org=None):
        with self.container:
            i = self.count_row(self.container)
            #name = f"{org["name"]}"
            with ui.expansion(text=f'{org["name"]}' if org else "New oranisation", caption=f'{org["domain"]}' if org else "domain", icon='work').classes('w-full') as row:
                self.org_content(org)
                ui.button('Удалить', on_click=lambda: self.container.remove(row))
    
    def count_row(self, element):
        return len(list(element)) 
    
    def org_content(self, organization):
        with ui.column().classes('w-full') as org:
            
            ui.label('Профили')
            if not organization:
                pass
            
            profiles = organization.get('Proffile', [])
            
            
            def add_profile():
                pass
            
            if len(profiles) == 0:
                add_profile()
            else:
                rows = [{'name': profile.get('name', ''), 'tag': profile.get('tag', ''), 
                'attribute': profile.get('attribute', ''), 'value': profile.get('value', ''), 
                'template': profile.get('template', ''), 'value_attribute': profile.get('value_attribute', '')} 
                for profile in organization.get('Proffile', [])]
                
                def handle_cell_value_change(e):
                    new_row = e.args['data']
                    ui.notify(f'Updated row to: {e.args["data"]}')
                    rows[:] = [row | new_row if row['id'] == new_row['id'] else row for row in rows]
                    
                aggrid = ui.aggrid({
                    'rowData': rows,
                    'columnDefs': [
                        {'field': 'name', 'headerName': 'Имя', 'editable': True},
                        {'field': 'tag', 'headerName': 'Тег', 'editable': True},
                        {'field': 'attribute', 'headerName': 'Атрибут', 'editable': True},
                        {'field': 'value', 'headerName': 'Значение', 'editable': True},
                        {'field': 'template', 'headerName': 'Шаблон', 'editable': True},
                        {'field': 'value_attribute', 'headerName': 'Атрибут значения', 'editable': True}
                    ],
                    'rowSelection': 'multiple',
                    'stopEditingWhenCellsLoseFocus': True,
                }).on('cellValueChanged', handle_cell_value_change)

            ui.button('Добавить профиль', on_click=add_profile)

            ui.label('URLs')
            urls = organization.get('Urls', [])
            
            def add_url():
                pass
            
            if len(urls) == 0:
                add_url()
            else:
                urls_table = [{'url': url} for url in urls]
                ui.table(rows=urls_table)

            ui.button('Добавить URL', on_click=add_url)
        return

    # def create_rows(self):
    #     for i in range(len(self.config['Organization'])):
    #         self.add_org(i)
    
    def add_button(self):
        ui.button('Добавить', on_click=lambda: self.add())
    
    def clear_button(self):
        ui.button('Очистить', on_click=self.container.clear)

# Создание страницы админ-панели
@ui.page('/admin')
def admin_page():
    ui.page_title('Админ-панель')
    
    try:
        with open('data.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        return
    
    ui.label('Организации').classes('font-bold')
    admin_page_organization = PageExpansion(ui.row())


    for _, organization in enumerate(config['Organization']):
        admin_page_organization.add(organization)

    admin_page_organization.add_button()
    admin_page_organization.clear_button()

    def save_config():
        new_config = {
            'Organization': []
        }

    ui.button('Сохранить', on_click=save_config)

# Создание формы для редактирования конфигурации
    
        
        
ui.run(favicon="🚀")