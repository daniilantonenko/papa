from db import *
from peewee import IntegrityError
from parsers import parse_page

class Organization(Organization):
    def __init__(self, name, domain, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call the parent class's __init__ method
        self.name = name
        self.domain = domain

    def scan(self):
         # Retrieve the Pages instance associated with this organization
        try:
            data = Pages.select().where(Pages.organization == self)
        except Pages.DoesNotExist:
            print("No pages found for this organization")
            return
       
        for d in data:
            cleare_data = parse_page(d.url)
            for item in cleare_data:
                try:
                    Product.create(
                        organization=self,
                        article=item['article'],
                        name=item['name'],
                        price=item['price'],
                        image=item['image']
                    )
                except IntegrityError:
                    print(f'[{item["article"]}] {item["name"]} - уже в базе')