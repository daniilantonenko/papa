from peewee import CharField, ForeignKeyField, Model

class Organization(Model):
    name = CharField(unique=True)
    domain = CharField()

class Product(Model):
    organization = ForeignKeyField(Organization)
    article = CharField(unique=True)
    name = CharField()
    price = CharField()
    image = CharField()

class Pages(Model):
    organization = ForeignKeyField(Organization)
    url = CharField(unique=True)