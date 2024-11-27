from models import Organization, Proffile, Page, Product
from utils import get_encoding_url, regex_extract, load_json, fetch_response, get_with_cache
import copy
from bs4 import BeautifulSoup
import aiohttp
import asyncio

async def save_to_database(data, progress=None):
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

                org_id =  Organization.create_or_update(**item_clear)

                for k, v in item.items():
                    if k == 'Proffile':
                        for p in v:
                            proffile_id = Proffile.create_or_update(organization=org_id,**p)
                            #print("proffile:", proffile_id)
                    elif k == 'Urls':
                        for u in v:
                             Page.create_or_update(organization=org_id, url=u)
                            #print("page:", page_id)
                    elif k == 'Sitemaps':
                        for s in v:
                            print("Start parse sitemap:", s)
                            links = await get_links_sitemap(url=s,filter=None,deepth=8,exclude=1)
                            # Check URLs status
                            urls_sitemap = await check_urls(links, progress)
                            urls_list = []
                            for url, status in zip(links, urls_sitemap):
                                if status == 200:
                                    urls_list.append(url)
                                    
                            # TODO: Передавать параметры filter, deepth, exclude
                            for l in urls_list:
                                #print(f'link: {l}')
                                 Page.create_or_update(organization=org_id, url=l)
                            print("End parse sitemap")
                            
async def scan(urls, organization):
    sum = 0
    for url in urls:
        page =  Page.create_or_update(organization=organization, url=url)
        if page is not None and page > 0:
            p = Page.get(id=page)
            

            # response = await get_with_cache(p.url)
            # if response is not None:
            #     soup = get_soup(response.text)
            #     p.save()
            # else:
            #     print(f"Page creation failed for {url}, response is None")
            #     continue
            
            page = await get_with_cache(p.url)
            if page is None:
                print(f"Page creation failed for {url}, response is None")
                continue
            data = get_soup(page.text)

            if data is not None:
                product = Product(organization=organization, page=p)
                count = await product.save_data(data=data)
                if count is not None:
                    sum += count
            else:
                print(f"No data found failed for {p.url}")
                continue
        else:
            print(f"Page creation failed for {url}")
            continue
    return sum

async def scan_all():
    sum = 0
    orgs = Organization.select()
    for org in orgs:
        urls = org.pages
        urls_list = [url.url for url in urls]
        count = await scan(urls_list, org)
        if count is not None:
                    sum += count
    return sum

def get_soup(data: str) -> BeautifulSoup:
    """
    Takes a string of HTML data and returns a BeautifulSoup object.

    Args:
        data (str): The HTML data to parse

    Returns:
        A BeautifulSoup object representing the parsed HTML
    """
    soup = BeautifulSoup(data, 'html.parser')
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
            if prefix:
                prefix += node.value + '/' 
            else:
                prefix += node.value + '//'
        if not node.children:
            # Получаем исключаемую часть пути в зависимости от значения exclude
            if exclude > 0:
                # Извлекаем последние элементы в количестве exclude для формирования ключа
                #suffix = '/'.join(prefix.strip('/').split('/')[-exclude:])+'/'
                prefix_without_suffix = '/'.join(prefix.strip('/').split('/')[:-exclude])
                # Добавляем уникальный адрес только если в urls ещё нет похожего с этим ключом
                if not any(url. startswith(prefix_without_suffix) for url in urls):
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
    r = await fetch_response(url)
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

sem = asyncio.Semaphore(10)  # limit to 10 concurrent requests

async def send_request(session, url,progress=None):
    async with sem:
        async with session.get(url, ssl=False) as response:
            #if progress:
            #    progress.update(1)
            return response.status

async def check_urls(urls,progress=None):
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, url, progress) for url in urls]
        results = await asyncio.gather(*tasks)
        #if progress:
        #    progress.close()
        return results

async def load_save_scan():
    # Load new data to database
    j = load_json('data.json')

    print('Saving data to database')
    await save_to_database(j)

    # Scan all Organizations
    print('Scanning all Organizations')
    await scan_all()

    print('Done!')

# TODO: catalog scanner