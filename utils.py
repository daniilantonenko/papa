import re
import requests
from urllib.parse import urlparse
    
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
    
def get_response(url):
    response = requests.get(url)
    return response

def download_file(url):
    url = re.sub(r'^(?!http://)//', 'http://', url)
    response = get_response(url)
    file_Path = 'images/' + url.split('/')[-1]

    if response.status_code == 200:
        with open(file_Path, 'wb') as file:
            file.write(response.content)
            return file_Path
    else:
        print('Failed to download file')

def get_domain(url):
    return urlparse(url).netloc
