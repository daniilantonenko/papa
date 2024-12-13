from nicegui import ui
from frontend.product import get_products

def content() -> None:
    ui.page_title('Каталог')

    products = get_products()

    products_per_page = 10
    products_quantity = len(products)
    max_page = (products_quantity + products_per_page - 1) // products_per_page

    products_page = products[:products_per_page]

    search = ui.input('Поиск').props('clearable')
    
    table = ui.table.from_pandas(products_page, row_key='id').props('grid')
    table.add_slot('item', r'''
        <q-card flat bordered :props="props" class="m-1 my-card">
            <q-card-section class="text-center">
                <strong>{{ props.row.name }}</strong>
            </q-card-section>
            <q-separator />
            <q-card-section class="text-center card-image">
                <a :href="'/product/' + props.row.id"><img :src="props.row.image ? props.row.image : 'static/blank.png'"></a>
            </q-card-section>
        </q-card>
    ''')

    p = ui.pagination(1, max_page, direction_links=True)

    def update_table():
        name = search.value
        p_value = p.value
        p_max = max_page
        
        if name == '' or not name:
            products_page = products[(p_value - 1) * products_per_page:p_value * products_per_page]
            return
        else:
            name = name.lower()
            filtered_products = products[products['name'].str.lower().str.contains(name, na=False)]
            products_page = filtered_products[(p_value - 1) * products_per_page:p_value * products_per_page]
            p_max = (len(filtered_products) + products_per_page - 1) // products_per_page
        
        table.update_from_pandas(products_page)
        p.max = p_max

    search.on_value_change(update_table)
    p.on_value_change(update_table)
    
    ui.add_css('''
        .my-card {
            width: 100%;
            max-width: 250px;
        }
        .card-image{
            overflow: hidden;
        }
    ''')
