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

# Создание страницы админ-панели
@ui.page('/admin')
def admin_page():
    # Создание веб-интерфейса
    ui.page_title('Админ-панель')
    # Загрузка конфигурации из файла
    try:
        with open('data.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        return
    
    with ui.card():
        ui.label('Организации').classes('font-bold')
        
        def add_organization():
            config['Organization'].append({'name': '', 'domain': '', 'Proffile': [], 'Urls': []})
            ui.notify('Организация добавлена')

        for i, organization in enumerate(config['Organization']):
            with ui.card() as card:
                ui.label(f'{organization['name']}').classes('font-bold my_card')
                ui.label(f'{organization['domain']}')
                ui.button('Удалить', on_click=lambda i=i: config['Organization'].pop(i) and card.delete()).props('icon=delete color=grey-5').classes('float-right')
                
                ui.label('Профили')
                profiles = organization.get('Proffile', [])
                
                def add_profile():
                    pass
                
                if len(profiles) == 0:
                    add_profile()
                else:
                    profiles_table = [{'name': profile.get('name', ''), 'tag': profile.get('tag', ''), 
                    'attribute': profile.get('attribute', ''), 'value': profile.get('value', ''), 
                    'template': profile.get('template', ''), 'value_attribute': profile.get('value_attribute', '')} 
                    for profile in organization.get('Proffile', [])]
                    
                    ui.table(rows=profiles_table)

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

        ui.button('Добавить организацию', on_click=add_organization)

        # Создание кнопки для сохранения конфигурации
        def save_config():
            new_config = {
                'Organization': []
            }
            # for i, organization in enumerate(config['Organization']):
            #     new_config['Organization'].append({
            #         'name': organization_name.value,
            #         'domain': organization_domain.value,
            #         'Proffile': [],
            #         'Urls': []
            #     })
            #     for j, profile in enumerate(organization['Proffile']):
            #         new_config['Organization'][i]['Proffile'].append({
            #             'name': profile_name.value,
            #             'tag': profile_tag.value,
            #             'attribute': profile_attribute.value,
            #             'value': profile_value.value,
            #             'template': profile_template.value,
            #             'value_attribute': profile_value_attribute.value
            #         })
            #     for k, url in enumerate(organization['Urls']):
            #         new_config['Organization'][i]['Urls'].append(url_input.value)
            # with open('config.json', 'w') as f:
            #     json.dump(new_config, f)
            # ui.notify('Конфигурация сохранена')

        ui.button('Сохранить', on_click=save_config)

    # Создание формы для редактирования конфигурации
    
        
        
ui.run(favicon="🚀")