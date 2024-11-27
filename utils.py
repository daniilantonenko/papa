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

async def fetch_response(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            print(f"Warning: Status code {response.status_code} for URL: {url}")
        return response
    except requests.exceptions.MissingSchema:
        print(f"Error: Invalid URL '{url}': No host supplied, URL: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error: requests exception: {e}, URL: {url}")
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Connection error for URL: {url}. {e}")
    return None

async def get_with_cache(url, cache_folder=cache_folder, cache_time=cache_time):
    filename = cache_folder + url.replace('/', '_')

    # Check if the file exists
    try:
        file_info = await aioos.stat(filename) 
        if time.time() - file_info.st_mtime > cache_time:
            print(f"Cache expired for {url}")
            os.remove(filename)
    except FileNotFoundError:
        pass

    try:
        # Check if the file is a file (not a directory)
        if await aioos.path.isfile(filename):
            # Read the file
            async with aiofiles.open(filename, 'rb') as f:
                print(f"Using cache for {url}")
                content = await f.read()
            r = requests.Response()
            r._content = content
            return r
        else:
            # File doesn't exist
            pass
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

    # If the file doesn't exist or is not a file, download it
    response = await fetch_response(url)
    if response is None:
        return None

    async with aiofiles.open(filename, 'wb') as f:
        print(f"Downloading {url} | {response.status_code}")
        await f.write(response.content)

    # Wait for the file to be written before returning
    await f.close()

    # Read the file
    async with aiofiles.open(filename, 'rb') as f:
        content = await f.read()
    r = requests.Response()
    r._content = content
    return r


async def download_file(url: str, directory: str):
    if url is None:
        return None

    allow_filetype = ('.jpg', '.png')
    if not url.endswith(allow_filetype):
        print(f'Disallowed downloading file type for {url}')
        return None

    url = re.sub(r'^//', 'http://', url)
    url = re.sub(r'^(?!(http|https)://)', 'http://', url)
    response = await fetch_response(url)
    file_path = directory + url.split('/')[-1]

    if response is not None:
        with open(file_path, 'wb') as file:
            file.write(response.content)
            return file_path
    else:
        print(f'Failed to download file from {url}')

def get_domain(url):
    return urlparse(url).netloc

def load_json(filename):
    with open(filename) as f:
        d = json.load(f)
        return d

async def get_encoding_url(response):
    encoding = chardet.detect(response.content)['encoding']
    return encoding