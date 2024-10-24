from peewee import *
from bs4 import BeautifulSoup
import requests
from parse import parse
import datetime

db = SqliteDatabase('./database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Organization(BaseModel):
    name = CharField(unique=True)
    domain = CharField()

    @classmethod
    def create_or_update(cls, name, domain):
        try:
            response = requests.head(domain, timeout=2)
            if response.status_code != 200:
                print(f"Missing domain status code for: {domain}")
        except requests.RequestException:
            print(f"Missing domain or unavailable 2 seconds: {domain}")

        org = cls.get_or_none(cls.name == name, cls.domain == domain)

        if org is None:
            organization_id = (Organization
                .insert(name=name, domain=domain)
                .on_conflict(
                    conflict_target=[Organization.name],
                    preserve=[Organization.id],
                    update={
                        Organization.domain: domain
                    }
                )
                .execute())
        else:
            organization_id = org.id

        return organization_id

class Proffile(BaseModel):
    organization = ForeignKeyField(Organization, backref='proffiles')
    name = CharField()  # Price
    tag = CharField()  # span
    attribute = CharField()  # class
    value = CharField(null=True)  # section-price
    template = CharField(null=True)  # \d[\d\w]*
    value_attribute = CharField(null=True)  # content

    class Meta:
        indexes = (
            (("organization", "name"), True),
        )

    @classmethod
    def create_or_update(cls, organization, name, tag, attribute, value=None, template=None, value_attribute=None):
        proffile = cls.get_or_none(cls.organization == organization, cls.name == name, cls.tag == tag, cls.attribute == attribute, cls.value == value, cls.template == template, cls.value_attribute == value_attribute)
        if proffile is None:
            proffile_id = (Proffile
                .insert(organization=organization, name=name, tag=tag, attribute=attribute, value=value, template=template, value_attribute=value_attribute)
                .on_conflict(
                    conflict_target=[Proffile.organization, Proffile.name],
                    preserve=[Proffile.id],
                    update={
                        Proffile.tag: tag,
                        Proffile.attribute: attribute,
                        Proffile.value: value,
                        Proffile.template: template,
                        Proffile.value_attribute: value_attribute
                    }
                )
                .execute())
        else:
            proffile_id = proffile.id
        return proffile_id

class Page(BaseModel):
    url = CharField(unique=True)
    organization = ForeignKeyField(Organization, backref='pages')

    @classmethod    
    def create_or_update(cls, organization, url):

        page = cls.get_or_none(cls.organization == organization, cls.url == url)

        if page is None:
            page_id = (Page
                .insert(organization=organization, url=url)
            .on_conflict(
                conflict_target=[Page.url],
                preserve=[Page.id],
                update={
                    Page.url: url
                }
            )
            .execute())
        else:
            page_id = page.id

        return page_id
    
    def scan(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            self.save()
            return soup
        except requests.RequestException as e:
            print(f"Failed to scan {self.url}: {e}")
            return None

class Product(BaseModel):
    organization = ForeignKeyField(Organization, backref='products')
    page = ForeignKeyField(Page, backref='products', unique=True)
    article = CharField(null=True)
    name = CharField(null=True)
    price = CharField(null=True)
    image = CharField(null=True)
    last_update = DateTimeField(default=datetime.datetime.now)

    @classmethod    
    def create_or_update(cls,organization,page,article,name,price,image):

        product = cls.get_or_none(cls.page == page)

        if product is None:
            product_id = (Product
                .insert(organization=organization, page=page,article=article,name=name,price=price,image=image)
            .on_conflict(
                conflict_target=[Product.page],
                preserve=[Product.id],
                update={
                    Product.article: article,
                    Product.name: name,
                    Product.price: price,
                    Product.image: image
                }
            )
            .execute())
        else:
            product_id = product.id

        return product_id

    def save_data(self, data):
        
        def find_by_proffile(proffile_name, data):
            try:
                proffile = Proffile.get(Proffile.organization == self.organization , Proffile.name == proffile_name)
                if proffile is None:
                    print(f"Proffile '{proffile_name}' not found for organization '{self.organization.name}'")
                    return
                element = data.find(proffile.tag, {proffile.attribute: proffile.value})
                if element is not None:
                    if proffile.value_attribute:
                        element = element.attrs.get(proffile.value_attribute, '')
                    text = element.text.strip() if hasattr(element, 'text') else element
                    return parse(text, proffile.template) if proffile.template else text
            except Proffile.DoesNotExist:
                print(f"Proffile '{proffile_name}' not found for organization '{self.organization.name}'")
            return None

        if data is not None:
            article = find_by_proffile("article", data)                
            name = find_by_proffile("name", data)
            price = find_by_proffile("price", data)
            image = find_by_proffile("image", data)
            url_image = self.organization.domain + image if image else ""
            
            product_id =  Product.create_or_update(self.organization, self.page, article, name, price, url_image)

            if product_id is None:
                print(f"Product not found for page '{self.page.url}'")
        else:
            print("No data found")

# TODO: add characteristics
# Table Characteristics
# organization
# product
# name
# value
# is_color

# Proffiles example:

# characteristics_name
# span
# itemprop = name

# characteristics_value
# span
# itemprop = value

db.connect()
db.create_tables([Organization, Product, Proffile, Page])