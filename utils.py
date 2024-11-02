import re
import requests
from urllib.parse import urlparse
import json
import chardet
    
def parse(string: str, template:str) -> str:
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
    
async def get_response(url):
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