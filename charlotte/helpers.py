"""Helper functions used in Charlotte.
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


def classify_content(url):
    """Attempts to categorize a website based on its HTML content. The
    most likely category (from the Google NLP API) will be returned as a
    string, or None.
    """
    if url:
        html_text = requests.get(url).text
        selector = Selector(text=html_text)
        # Find our first occurence of an <article>
    return None