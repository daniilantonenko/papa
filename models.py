from peewee import *
from utils import *
import datetime

db = SqliteDatabase('./database.db')

class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def create_or_update(cls, **kwargs):
        try:
            # Фильтруем условия только с полями, которые есть в модели
            conditions = {field: value for field, value in kwargs.items() if hasattr(cls, field)}

            # Проверяем наличие записи по этим условиям
            instance = cls.get_or_none(**conditions)

            if instance:
                # Если запись найдена, обновляем её
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                instance.save()
                return instance.id
            else:
                # Иначе создаём новую запись
                instance = cls.create(**kwargs)
                return instance.id

        except Exception as e:
            print(f"Error in {cls.__name__}.create_or_update: {e}")
            return None

class Organization(BaseModel):
    name = CharField(unique=True)
    domain = CharField()

class Proffile(BaseModel):
    organization = ForeignKeyField(Organization, backref='proffiles')
    name = CharField()  # Price
    tag = CharField()  # span
    attribute = CharField(null=True)  # class
    value = CharField(null=True)  # section-price
    template = CharField(null=True)  # \d[\d\w]*
    value_attribute = CharField(null=True)  # content
    disable = TextField(null=True)

    # NOT WORKING:

    #                 "disable": [
    #                     "Торговая марка",
    #                     "Цвет основ."
    #                 ]

    class Meta:
        indexes = (
            (("organization", "name"), True),
        )

class Page(BaseModel):
    url = CharField(unique=True)
    organization = ForeignKeyField(Organization, backref='pages')

class Characteristics(BaseModel):
    organization = ForeignKeyField(Organization, backref='organizations')
    proffile = ForeignKeyField(Proffile, backref='proffiles')
    product = DeferredForeignKey('Product', backref='characteristics')
    name = CharField(null=True)
    value = CharField(null=True)
    is_color = BooleanField(default=False)
    disable = BooleanField(default=False)

    class Meta:
        indexes = (
            (("organization", "name", "product"), True),
        )

class Product(BaseModel):
    organization = ForeignKeyField(Organization, backref='products')
    page = ForeignKeyField(Page, backref='products', unique=True)
    article = CharField(null=True)
    name = CharField(null=True)
    price = CharField(null=True)
    image = CharField(null=True)
    last_update = DateTimeField(default=datetime.datetime.now)

    async def save_data(self, data):
        
        def find_by_proffile(proffile_name, data):
            try:
                proffile = Proffile.get(Proffile.organization == self.organization , Proffile.name == proffile_name)
                if proffile is None:
                    print(f"Proffile '{proffile_name}' not found for organization '{self.organization.name}'")
                    return
                if proffile.attribute:
                    element = data.find(proffile.tag, {proffile.attribute: proffile.value})
                else:
                    element = data.find(proffile.tag)
                if element is not None:
                    if proffile.value_attribute:
                        element = element.attrs.get(proffile.value_attribute, '')
                    text = element.text.strip() if hasattr(element, 'text') else element
                    return parse(text, proffile.template) if proffile.template else text
            except Proffile.DoesNotExist:
                print(f"Proffile '{proffile_name}' not found for organization '{self.organization.name}'")
            return None
        
        def find_by_proffile_table(table, name, value, data, product_id):
            # Получаем Proffile для таблицы, имени и значения
            priffile_table = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == table)
            if priffile_table is None:
                #print(f"Proffile '{table}' not found for organization '{self.organization.name}'")
                return None

            proffile_name = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == name)
            if proffile_name is None:
                print(f"Proffile '{name}' not found for organization '{self.organization.name}'")
                return None

            proffile_value = Proffile.get_or_none(Proffile.organization == self.organization, Proffile.name == value)
            if proffile_value is None:
                print(f"Proffile '{value}' not found for organization '{self.organization.name}'")
                return None
            
            # Поиск элемента таблицы
            element_table = data.find(priffile_table.tag, {priffile_table.attribute: priffile_table.value})
            if element_table is None:
                #print(f"element_table not found for organization '{self.organization.name}'")
                #print(f'proffile_table: {priffile_table}, proffile_name: {proffile_name}, proffile_value: {proffile_value}')
                return None
            
            #print(f"Table '{table}' found for organization '{self.organization.name}'")
            
            # Найдем все элементы таблицы
            characteristics_elements = element_table.find_all('td')
            if not characteristics_elements:
                print(f"No characteristics found for organization '{self.organization.name}'")
                return []
            
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
            
                if proffile_name.disable and element_name in proffile_name.disable:
                    disable = True
                else:
                    disable = False

                # Создание или обновление характеристики
                characteristic, created = Characteristics.get_or_create(
                    organization=self.organization,
                    proffile=proffile_name,
                    product=product_id,
                    name=element_name,
                    value=element_value,
                    is_color=False,
                    disable=disable
                )
                if not created:
                    characteristic.value = element_value
                    characteristic.disable = disable
                    characteristic.save()

        if data is not None:
            article = find_by_proffile("article", data)                
            name = find_by_proffile("name", data)
            price = find_by_proffile("price", data)
            image = find_by_proffile("image", data)

            image_domain = get_domain(image)

            if image is not None:
                if image_domain is not None and image_domain != '':
                    url_image = "/" + await download_file(image)
                else:
                    if self.organization.domain is not None:
                        url_image = "/" + await download_file(self.organization.domain + image)
                    else:
                        print(f"Image domain not found")
                        url_image = None
            else:
                url_image = None

            product_id = Product.create_or_update(
                organization=self.organization,
                page=self.page,
                article=article,
                name=name,
                price=price,
                image=url_image
            )

            characteristics_list = find_by_proffile_table("characteristics_table","characteristics_name","characteristics_value", data,product_id)
    

            if product_id is None:
                print(f"Product not found for page '{self.page.url}'")
        else:
            print("No data found")

db.connect()
db.create_tables([
    Organization, 
    Proffile, 
    Page,
    Characteristics,
    Product])