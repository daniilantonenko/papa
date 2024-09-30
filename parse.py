import re

def parse_price(price_str):
    match = re.search(r'(\d[\d\s]*)', price_str)
    if match:
        price = match.group(1)
        price = price.replace(' ', '')
        return price
    else:
        return None
    
def parse_article(article_str):
    match = re.search(r'(\d[\d\w]*)', article_str)
    if match:
        article = match.group(1)
        article = article.replace(' ', '')
        return article
    else:
        return None
