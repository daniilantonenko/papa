import re
    
def parse(string: str, template:str) -> str:
    """
    :param string: string contains data
    :param template: template string
    :return: cleaned string
    """
    match = re.search(template, string)
    if match:
        article = match.group(1)
        article = article.replace(' ', '')
        return article
    else:
        return None
