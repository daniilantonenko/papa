from peewee import *
from utils import get_domain, regex_extract, download_file, find_html, extract_chars
import datetime

db = SqliteDatabase('./database.db')

class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def create_or_update(cls, **kwargs):
        try:
            # Фильтруем условия только с полями, которые есть в модели
            indexes_fields = [field for field in cls._meta.indexes[0][0] if field in kwargs]
            conditions = {field: kwargs[field] for field in indexes_fields}

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
            print(kwargs)
            return None

    def delete(self):
        try:
            self.delete_instance()
        except Exception as e:
            print(f"Error in {self.__class__.__name__}.delete: {e}")
            
class Organization(BaseModel):
    name = CharField(unique=True)
    domain = CharField()

    class Meta:
        indexes = (
            (("name",), True),
        )

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

    class Meta:
        indexes = (
            (("url","organization"), True),
        )

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
        
        def get_proffile(proffile_name: str) -> Proffile | None:
            try:
                proffile = Proffile.get(Proffile.organization == self.organization , Proffile.name == proffile_name)
                return proffile
            except Proffile.DoesNotExist:
                print(f"Proffile '{proffile_name}' not found for organization '{self.organization.name}'")
            return None
        
        def find_by_proffile(proffile_name: str, data):
            proffile = get_proffile(proffile_name)
            if proffile is None:
                return None
            return find_html(proffile,data)

        if data is not None:
            article = find_by_proffile("article", data)
            name = find_by_proffile("name", data)
            price = find_by_proffile("price", data)
            image = find_by_proffile("image", data)

            image_domain = get_domain(image)

            if image is not None:
                if image_domain is not None and image_domain != '':
                    file = await download_file(image,'images/')
                    if file is not None:
                        url_image = "/" + await download_file(image,'images/')
                    else:
                        url_image = None
                else:
                    if self.organization.domain is not None:
                        file = await download_file(self.organization.domain + image,'images/')
                        if file is not None:
                            url_image = "/" + file
                        else:
                            url_image = None
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

            #characteristics_list = find_by_proffile_table("characteristics_table","characteristics_name","characteristics_value", data,product_id)
            chars_table_proffile = get_proffile("characteristics_table")
            chars_name_proffile = get_proffile("characteristics_name")
            chars_value_proffile = get_proffile("characteristics_value")

            characteristics_list = extract_chars(data, chars_table_proffile, chars_name_proffile, chars_value_proffile)

            if characteristics_list is not None:
                for name, value in characteristics_list.items():
                    Characteristics.create_or_update(
                        organization=self.organization,
                        proffile=chars_name_proffile,
                        product=product_id,
                        name=name,
                        value=value,
                        is_color=False,
                        disable=False
                    )

            if product_id is None:
                print(f"Product not found for page '{self.page.url}'")
        else:
            print("No data found")

    class Meta:
        indexes = (
            (("organization","page"), True),
        )

db.connect()
db.create_tables([
    Organization, 
    Proffile, 
    Page,
    Characteristics,
    Product])