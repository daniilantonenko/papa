from peewee import *
from models import *


db = SqliteDatabase('./database.db')

class Organization(Organization):
    class Meta:
        database = db

class Product(Product):
    class Meta:
        database = db

class Pages(Pages):
    class Meta:
        database = db

db.connect()
db.create_tables([Organization, Product, Pages])
