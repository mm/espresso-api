"""Tests the built-in Twitter parser.
"""

from src.tweet.service import TwitterService
import pytest


@pytest.mark.parametrize(
    "url",
    [
        "https://twitter.com/TwitterDev/status/1271111223220809728",
        "https://twitter.com/TwitterDev/status/1271111223220809728?s=15",
    ],
)
def test_parse_id_from_url(url):
    id = TwitterService().parse_tweet_id_from_url(url)
    assert id == "1271111223220809728"
