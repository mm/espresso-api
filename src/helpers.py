"""Helper functions used in Espresso.
"""

import requests
from parsel import Selector

def extract_title_from_url(url):
    """Attempts to extract the title from a website using
    its <title> tag, or None if not possible.
    """
    
    if url:
        html_text = requests.get(url).text
        selector = Selector(text=html_text)
        title = selector.xpath('//title/text()').get()
        if title:
            title = title.strip()
        return title
    return None