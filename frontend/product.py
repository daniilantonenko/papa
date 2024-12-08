from models import Product
import pandas as pd

# Define a function to get product data from your data store
def get_product(id):
    product = Product.get(id=id)

    return product

def get_charecteristics(product_id):
    characteristics = Product.get(Product.id == product_id).characteristics
    if characteristics is None or len(characteristics) == 0:
        return None
    return pd.DataFrame(list(characteristics.dicts()))
 
def get_quantity():
    quantity = Product.select().count()
    return quantity

def get_products():
    products = Product.select()
    products = pd.DataFrame(list(products.dicts()))
    return products