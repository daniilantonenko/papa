from peewee import IntegrityError
from parsers import parse_page
from db import Product


def scan(url):
    # Парсинг HTML
    data = parse_page(url)

    # Сохраняем данные в базе
    for item in data:
        if 'organization' in item and 'article' in item and 'name' in item and 'price' in item and 'image' in item:
            try:
                Product.create(
                    organization=item['organization'],
                    article=item['article'],
                    name=item['name'],
                    price=item['price'],
                    image=item['image']
                )
                print(f'[{item["article"]}] {item["name"]} - сохранена в базе')
            except IntegrityError:
                print(f'[{item["article"]}] {item["name"]} - уже в базе')
        else:
            print("Недостаточно данных для записи")
            
urls = ['https://www.stan.su/catalog/odezhda_1/futbolka/',
        'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/',
        'https://www.stan.su/catalog/odezhda_1/rubashka_polo/']

for u in urls:
    scan(u)