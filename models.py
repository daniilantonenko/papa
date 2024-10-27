from peewee import *
from bs4 import BeautifulSoup
import requests
from parse import parse
import datetime
import json

db = SqliteDatabase('./database.db')

class BaseModel(Model):
    class Meta:
        database = db

    # TODO: def create_or_update(self, **kwargs):

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
    disable = TextField(null=True)

    class Meta:
        indexes = (
            (("organization", "name"), True),
        )

    @classmethod
    def create_or_update(cls, organization, name, tag, attribute, value=None, template=None, value_attribute=None, disable=None):
        proffile = cls.get_or_none(cls.organization == organization, cls.name == name, cls.tag == tag, cls.attribute == attribute, cls.value == value, cls.template == template, cls.value_attribute == value_attribute)
        if proffile is None:
            proffile_id = (Proffile
                .insert(organization=organization, name=name, tag=tag, attribute=attribute, value=value, template=template, value_attribute=value_attribute, disable=disable)
                .on_conflict(
                    conflict_target=[Proffile.organization, Proffile.name],
                    preserve=[Proffile.id],
                    update={
                        Proffile.tag: tag,
                        Proffile.attribute: attribute,
                        Proffile.value: value,
                        Proffile.template: template,
                        Proffile.value_attribute: value_attribute,
                        Proffile.disable: disable
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

# TODO: add characteristics
# Table Characteristics
# organization = 1
# proffile = 13
# name = Цвет
# values = Белый, Черный, Красный
# is_color = True

# Proffiles example:

# characteristics_name
# span
# itemprop = name

# characteristics_value
# span
# itemprop = value

class Characteristics(BaseModel):
    organization = ForeignKeyField(Organization, backref='characteristics')
    proffile = ForeignKeyField(Proffile, backref='proffiles')
    name = CharField()
    value = TextField()
    is_color = BooleanField(default=False)
    disable = BooleanField(default=False)

    class Meta:
        indexes = (
            (("organization", "name"), True),
        )

    @classmethod
    def create_or_update(cls, organization, proffile, name, value, is_color,disable):
        characteristics = cls.get_or_none(cls.organization == organization, cls.proffile == proffile, cls.name == name, cls.value == value, cls.is_color == is_color, cls.disable == disable)
        if characteristics is None:
            characteristics_id = (Characteristics
                .insert(organization=organization, proffile=proffile, name=name, value=value, is_color=is_color, disable=disable)
                .on_conflict(
                    conflict_target=[Characteristics.organization, Characteristics.name],
                    preserve=[Characteristics.id],
                    update={
                        Characteristics.value: value,
                        Characteristics.is_color: is_color,
                        Characteristics.disable: disable
                    }
                )
                .execute())
        else:
            characteristics_id = characteristics.id
        return characteristics_id

class Product(BaseModel):
    organization = ForeignKeyField(Organization, backref='products')
    page = ForeignKeyField(Page, backref='products', unique=True)
    article = CharField(null=True)
    name = CharField(null=True)
    price = CharField(null=True)
    image = CharField(null=True)
    characteristics = ManyToManyField(Characteristics, backref='products')
    last_update = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def create_or_update(cls, organization, page, article, name, price, image, characteristics_list=None):
        product = cls.get_or_none(cls.page == page)

        if product is None:
            # Создание нового продукта
            product = cls.create(
                organization=organization,
                page=page,
                article=article,
                name=name,
                price=price,
                image=image
            )
        else:
            # Обновление существующего продукта
            product.article = article
            product.name = name
            product.price = price
            product.image = image
            product.save()

        # Обновление характеристик
        # Сначала удаляем старые связи, затем добавляем новые
        product.characteristics.clear()
        product.characteristics.add(characteristics_list)

        return product.id

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
        
        def find_by_proffile_table(table, name, value, data, **kwargs):
            # Получаем Proffile для таблицы, имени и значения
            priffile_table = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == table)
            if priffile_table is None:
                print(f"Proffile '{table}' not found for organization '{self.organization.name}'")
                return []

            proffile_name = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == name)
            if proffile_name is None:
                print(f"Proffile '{name}' not found for organization '{self.organization.name}'")
                return []

            proffile_value = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == value)
            if proffile_value is None:
                print(f"Proffile '{value}' not found for organization '{self.organization.name}'")
                return []

            # Поиск элемента таблицы
            element_table = data.find(priffile_table.tag, {priffile_table.attribute: priffile_table.value})
            if element_table is None:
                print(f"Table not found")
                return []

            # Найдем все элементы таблицы
            characteristics_elements = element_table.find_all('td')
            if not characteristics_elements:
                print(f"No characteristics found for organization '{self.organization.name}'")
                return []

            characteristics_list = []
            # Проходим по элементам, по два за раз (имя и значение)
            for i in range(0, len(characteristics_elements), 2):
                name_element = characteristics_elements[i].find('span', itemprop="name")
                element_name = name_element.text.strip() if name_element and hasattr(name_element, 'text') else None
                if not element_name:
                    continue

                value_element = characteristics_elements[i + 1].find('span', itemprop="value")
                element_value = value_element.text.strip() if value_element and hasattr(value_element, 'text') else None
                if not element_value:
                    continue

                if element_name in proffile_name.disable:
                    disable = True
                else:
                    disable = False

                # Создание или обновление характеристики
                characteristic, created = Characteristics.get_or_create(
                    organization=self.organization,
                    proffile=proffile_name,
                    name=element_name,
                    defaults={'value': element_value, 'is_color': False, 'disable': disable}
                )
                if not created:
                    characteristic.value = element_value
                    characteristic.disable = disable
                    characteristic.save()

                # Добавляем в список
                characteristics_list.append(characteristic)

            return characteristics_list


        if data is not None:
            article = find_by_proffile("article", data)                
            name = find_by_proffile("name", data)
            price = find_by_proffile("price", data)
            image = find_by_proffile("image", data)
            characteristics_list = find_by_proffile_table("characteristics_table","characteristics_name","characteristics_value", data)
            url_image = self.organization.domain + image if image else ""
            
            product_id =  Product.create_or_update(self.organization, self.page, article, name, price, url_image,characteristics_list)

            if product_id is None:
                print(f"Product not found for page '{self.page.url}'")
        else:
            print("No data found")

ProductCharacteristics = Product.characteristics.get_through_model()

db.connect()
db.create_tables([Organization, Product, Proffile, Page, Characteristics, ProductCharacteristics])