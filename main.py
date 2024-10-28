from models import *
   
def scan(urls, organization):
    for url in urls:
        page = Page.create_or_update(organization=organization, url=url)
        if page is not None and page > 0:
            p = Page.get(id=page)
            data = p.scan()

            if data is not None:
                product = Product(organization=organization, page=p)
                product.save_data(data=data)
            else:
                print(f"No data found failed for {p.url}")
                return
        else:
            print(f"Page creation failed for {url}")
            return

org = Organization.create_or_update(
     name='STAN', 
     domain='https://www.stan.su')

prof_price = Proffile.create_or_update(
    organization=org,
    name='price',
    tag='meta',
    attribute='itemprop',
    value='price',
    template=r'(\d[\d\s]*)',
    value_attribute='content'
)

proffile_article = Proffile.create_or_update(
    organization=org,
    name='article',
    tag='span',
    attribute='class',
    value='article_element',
    template=r'(\d[\d\w]*)'
)

proffile_name = Proffile.create_or_update(
    organization=org,
    name='name',
    tag='h1',
    attribute='id',
    value='pagetitle',
    template=r"^(.*?)\sSTAN\s(.*?)(?=,)"
)
     
proffile_image = Proffile.create_or_update(
    organization=org,
    name='image',
    tag='img',
    attribute='class',
    value='product-detail-gallery__picture',
    value_attribute='data-src'
)  

proffile_charecteristics_table = Proffile.create_or_update(
    organization=org,
    name='characteristics_table',
    tag='table',
    attribute='class',
    value='props_list'
)

proffile_charecteristics_name = Proffile.create_or_update(
    organization=org,
    name='characteristics_name',
    tag='span',
    attribute='itemprop',
    value='value',
    disable=["Торговая марка","Цвет основ."]
)

proffile_charecteristics_value = Proffile.create_or_update(
    organization=org,
    name='characteristics_value',
    tag='span',
    attribute='itemprop',
    value='value'
)

test_urls = ['https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/bomber_70/898642/',
            'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/bomber_71/898754/',
            'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/tolstovka_95/803848/',
            'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/tolstovka_65n/799055/',
            'https://www.stan.su/catalog/odezhda_1/bombery_i_olimpiyki/tolstovka_65/202007/']

scan(test_urls, org)

# TODO: catalog scanner