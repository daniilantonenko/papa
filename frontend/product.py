from models import Product
import pandas as pd

# Define a function to get product data from your data store
def get_product(id) -> Product:
    try:
        product = Product.get(id=id)
        return product
    except:
        return None

def get_quantity() -> int:
    quantity = Product.select().count()
    return quantity

def get_products() -> pd.DataFrame:
    products = Product.select()
    products = pd.DataFrame(list(products.dicts()))
    return products