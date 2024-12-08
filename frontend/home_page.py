from nicegui import ui
from frontend.product import get_products, get_quantity

def content() -> None:
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
                <a :href="'/product/' + props.row.id"><img :src="props.row.image ? props.row.image : 'static/blank.png'"></a>
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
