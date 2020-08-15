"""
Unit tests to run on any helper functions Charlotte depends on.
"""

import pytest

from charlotte.helpers import extract_title_from_url


@pytest.mark.parametrize(('url', 'title'), (
    ('https://google.ca', 'Google'),
    ('https://mascioni.ca', 'Matthew Mascioni'),
    ('', None),
    (None, None)
))
def test_extracting_url_title(url, title):
    extracted_title = extract_title_from_url(url)
    assert extracted_title == title
