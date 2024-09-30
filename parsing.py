import requests
from bs4 import BeautifulSoup
import sqlite3
# Переписать на https://github.com/coleifer/peewee
from parse import parse_price,parse_article 

def scan(url):
    # Парсинг HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем необходимые данные
    data = soup.find_all('div', class_='section-compact-list__item')

    cleaned_data = []
    for item in data:
        organization = 'STAN'
        article = item.find('div', class_='article_model').text.strip()
        article = parse_article(article)
        name = item.find('a', class_='section-compact-list__link').span.text
        price = item.find('span', class_='section-price').text.strip()
        parsed_price = parse_price(price)
        image = "https://www.stan.su" + item.find('img', class_='img-responsive')['data-src']

        cleaned_item = {
            'organization': organization,
            'article': article,
            'name': name,
            'price': parsed_price,
            'image': image,
        }
        cleaned_data.append(cleaned_item)

    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('c:/Users/DNS1/Desktop/my_database.db')

    cursor = connection.cursor()

    try:
        # Создаем таблицу, если она не существует
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                organization TEXT,
                article TEXT,
                name TEXT,
                price TEXT,
                image TEXT
            )
        ''')
        
        # Создаем SQL запрос на вставку данных
        sql = "INSERT INTO products (organization, article, name, price, image) VALUES (?, ?, ?, ?, ?)"
        for item in cleaned_data:
            cursor.execute(sql, (item['organization'], item['article'], item['name'], item['price'], item['image']))
        
        # Сохраняем изменения
        connection.commit()

    finally:
        cursor.close()
        connection.close()

urls = ['https://www.stan.su/catalog/odezhda_1/futbolka/',
        'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/',
        'https://www.stan.su/catalog/odezhda_1/rubashka_polo/']

for u in urls:
    scan(u)


