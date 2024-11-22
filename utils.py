import re
import requests
from urllib.parse import urlparse
import json
import chardet
import aiofiles
import aiofiles.os as aioos
import time
import os

cache_folder = 'cache/'
os.makedirs(cache_folder, exist_ok=True)
cache_time = 3600

def find_html(self, data):
        """
        Find and extract data from HTML.

        Find an element in the HTML using the tag, attribute and value.
        If the element is found, extract the text from the element
        and apply the regex template to it if specified.

        Args:
            data (BeautifulSoup): The HTML to search in

        Returns:
            str: The extracted text
        """
        if hasattr(self, "attribute") and self.attribute:
            element = data.find(self.tag, {self.attribute: self.value})
        else:
            element = data.find(self.tag)
        if element is not None:
            if hasattr(self, "value_attribute") and self.value_attribute:
                element = element.attrs.get(self.value_attribute, '')
            text = element.text.strip() if hasattr(element, 'text') else element
            return regex_extract(text, self.template) if hasattr(self, "template") and  self.template else text
    
def regex_extract(string: str, template:str) -> str:
    """
    :param string: string contains data
    :param template: template string
    :return: cleaned string
    """
    match = re.search(template, string)
    if match: 
        string = " ".join(match.groups())
        return string.strip()
    else:
        return None

async def fetch_response(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Warning: Status code {response.status_code} for URL: {url}")
        return response
    except requests.exceptions.MissingSchema:
        print(f"Error: Invalid URL '{url}': No host supplied, URL: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}, URL: {url}")
    return None

async def get_response(url, cache_folder=cache_folder, cache_time=cache_time):
    filename = cache_folder + url.replace('/', '_')
    try:
        file_info = await aioos.stat(filename)
        if time.time() - file_info.st_mtime > cache_time:
            os.remove(filename)
            raise FileNotFoundError
    except FileNotFoundError:
        response = await fetch_response(url)
        if response is None:
            return None
        async with aiofiles.open(filename, 'wb') as f:
            await f.write(response.content)
    else:
        async with aiofiles.open(filename, 'rb') as f:
            content = await f.read()
            r = requests.Response()
            r._content = content
            return r

async def download_file(url):
    if url is None:
        return
    url = re.sub(r'^(?!http://)//', 'http://', url)
    response = await get_response(url)
    file_Path = 'images/' + url.split('/')[-1]

    if response is not None:
        with open(file_Path, 'wb') as file:
            file.write(response.content)
            return file_Path
    else:
        print('Failed to download file')

def get_domain(url):
    return urlparse(url).netloc

def load_json(filename):
    with open(filename) as f:
        d = json.load(f)
        return d

async def get_encoding_url(response):
    encoding = chardet.detect(response.content)['encoding']
    return encoding