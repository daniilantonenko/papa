from models import *
import copy
from bs4 import BeautifulSoup
from utils import get_response, get_encoding_url


async def save_to_database(data):
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

                key_to_remove3 = 'Sitemaps'
                if key_to_remove3 in item_clear:
                    item_clear.pop(key_to_remove3)

                org_id = await Organization.create_or_update(**item_clear)
                #print("organization:", org_id)

                for k, v in item.items():
                    if k == 'Proffile':
                        for p in v:
                             Proffile.create_or_update(organization=org_id,**p)
                            #print("proffile:", proffile_id)
                    elif k == 'Urls':
                        for u in v:
                             Page.create_or_update(organization=org_id, url=u)
                            #print("page:", page_id)
                    elif k == 'Sitemaps':
                        for s in v:
                            links = await get_links_sitemap(url=s,filter=None,deepth=8,exclude=1)
                            # TODO: Передавать параметры filter, deepth, exclude
                            for l in links:
                                #print(f'link: {l}')
                                Page.create_or_update(organization=org_id, url=l)
                            
async def scan(urls, organization):
    for url in urls:
        page = Page.create_or_update(organization=organization, url=url)
        if page is not None and page > 0:
            p = Page.get(id=page)

            response = await get_response(p.url)
            if response is not None:
                soup = get_soup(response)
                p.save()
            else:
                print(f"Page creation failed for {url}, response is None")
                return
        
            data = soup

            if data is not None:
                product = Product(organization=organization, page=p)
                await product.save_data(data=data)
            else:
                print(f"No data found failed for {p.url}")
                return
        else:
            print(f"Page creation failed for {url}")
            return

async def scan_all():
    orgs = Organization.select()
    for org in orgs:
        urls = org.pages
        urls_list = [url.url for url in urls]
        await scan(urls_list, org)

def get_soup(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.children = {}

    def add_child(self, value):
        if value not in self.children:
            self.children[value] = Node(value)
            self.children[value].parent = self
        return self.children[value]

class BinaryTreeUrls:
    def __init__(self):
        self.root = Node('')

    def add_url(self, url, exclude=0):
        elements = url.split('/')
        current_node = self.root
        for element in elements:
            if element and not (exclude > 0 and len(elements) - elements.index(element) < exclude + 1):
                current_node = current_node.add_child(element)

    def get_all_urls(self, exclude=0):
        """
        Traverses the binary tree of URLs and retrieves all unique URLs.

        This function starts from the root node and traverses the tree to
        collect all possible URLs, optionally excluding a specified number
        of trailing path elements for uniqueness. 

        Args:
            exclude (int): The number of trailing path elements to ignore
                for uniqueness. If greater than 0, URLs are considered 
                unique based on the remaining path elements after exclusion.

        Returns:
            list: A list of unique URLs generated from the binary tree.
        """
        return self._get_all_urls(self.root, '', [], exclude)

    def _get_all_urls(self, node, prefix, urls, exclude):
        if node.value:
            prefix += node.value + '/'
        if not node.children:
            # Получаем исключаемую часть пути в зависимости от значения exclude
            if exclude > 0:
                # Извлекаем последние элементы в количестве exclude для формирования ключа
                #suffix = '/'.join(prefix.strip('/').split('/')[-exclude:])+'/'
                prefix_without_suffix = '/'.join(prefix.strip('/').split('/')[:-exclude])
                # Добавляем уникальный адрес только если в urls ещё нет похожего с этим ключом
                if not any(url. startswith(prefix_without_suffix) for url in urls):
                    urls.append(prefix)
                    #print(prefix)
            else:
                urls.append(prefix)
        else:
            for child in node.children.values():
                self._get_all_urls(child, prefix, urls, exclude)
        return urls
    
    def print_tree(self, node=None, level=0):
        node = node or self.root
        print('  ' * level + str(node.value))
        for child in node.children.values():
            self.print_tree(child, level + 1)

async def get_links_sitemap(url,filter=None,deepth=None,exclude=None):
    """
    Downloads a sitemap and parses it to retrieve all URLs.

    Args:
        url (str): The URL of the sitemap to download and parse.
        filter (str): An optional string to filter the URLs by.
        deepth (int): An optional integer to filter the URLs by.
        exclude (int): An optional integer to filter the URLs by.
    """
    r = await get_response(url)
    if r is None:
        print(f"Страница sitemap {url} не существует")
        return
        
    encoding = await get_encoding_url(r)
    try:
        soup = BeautifulSoup(r.content.decode(encoding, errors='ignore'), 'xml')
    except UnicodeDecodeError as e:
        print(f"Ошибка декодирования: {e}. Кодировка: {encoding}")
        return

    links = [item.text for item in soup.select("loc")]

    tree = BinaryTreeUrls()
    for link in links:
        r = await get_response(link)
        # Пропускаем ссылки, которые не возвращают 200 код
        if r is None:
            print(f"Страница {link} не существует")
            continue
        else:
            # TODO filter: if filter is not None and filter in link
            #print(f'Link:{link},deepth:{deepth}')
            if deepth is not None and deepth > 0:
                if link.count("/") == deepth:
                    tree.add_url(link)
                else:
                    continue
                    #tree.add_url(link)
    tree_urls = tree.get_all_urls(exclude=exclude)
    if tree_urls is not None:
        return tree_urls
    return None

# TODO: catalog scanner