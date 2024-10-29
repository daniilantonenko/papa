from models import *
import json
import copy

def load_json(filename):
    with open(filename) as f:
        d = json.load(f)
        return d

def parse_to_models(data):
    for key, value in data.items():
        if key == 'Organization':
            for item in value:

                item_clear = copy.deepcopy(item)
                key_to_remove = 'Proffile'
                if key_to_remove in item_clear:
                    item_clear.pop(key_to_remove)
                
                key_to_remove2 = 'Urls'
                if key_to_remove2 in item_clear:
                    item_clear.pop(key_to_remove2)

                org_id = Organization.create_or_update(**item_clear)
                #print("organization:", org_id)

                for k, v in item.items():
                    if k == 'Proffile':
                        for p in v:
                            proffile_id = Proffile.create_or_update(organization=org_id,**p)
                            #print("proffile:", proffile_id)
                    elif k == 'Urls':
                        for u in v:
                            page_id = Page.create_or_update(organization=org_id, url=u)
                            #print("page:", page_id)

def scan(urls, organization):
    for url in urls:
        #print(organization, url)
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

def multi_scan():
    orgs = Organization.select()
    for org in orgs:
        urls = org.pages
        urls_list = [url.url for url in urls]
        scan(urls_list, org)

j = load_json('data.json')
parse_to_models(j)

multi_scan()

# TODO: catalog scanner