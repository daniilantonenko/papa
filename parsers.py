from bs4 import BeautifulSoup
import requests
from parse import parse_price,parse_article 


def parse_page(url):
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

    return cleaned_data
