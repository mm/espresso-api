"""Tests the built-in Twitter parser.
"""

from unittest.mock import patch
from dateutil.parser import isoparse
from src.tweet.service import TwitterService
import pytest

SAMPLE_API_OUTPUT_JSON = {
    "data": {
        "conversation_id": "1377296544047587329",
        "id": "1377296544047587329",
        "text": "Over a year ago, we released the COVID-19 stream to help people build resources for the public good.\n\nNow we're sharing more about how people used this data to study everything from misinformation, to how attitudes about the virus evolved over time. \uD83D\uDCA1\n\nhttps://t.co/ANU9rza3l4",
        "author_id": "2244994945",
        "created_at": "2021-03-31T16:27:39.000Z",
    },
    "includes": {
        "users": [{"id": "2244994945", "name": "Twitter Dev", "username": "TwitterDev"}]
    },
}


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


def test_parse_tweet_by_id():
    """The service should be able to turn a tweet response from the Twitter API
    into a Tweet object, with the correct properties populated.
    """

    with patch("src.tweet.service.TwitterService.make_get_request") as mock_get_request:
        mock_get_request.return_value.json.return_value = SAMPLE_API_OUTPUT_JSON
        mock_get_request.return_value.status_code = 200
        tweet = TwitterService().get_tweet_by_id("1377296544047587329")
        assert tweet.title == "Tweet by @TwitterDev"
        assert tweet.text == SAMPLE_API_OUTPUT_JSON["data"]["text"]
        assert (
            tweet.conversation_id == SAMPLE_API_OUTPUT_JSON["data"]["conversation_id"]
        )
        assert tweet.created_date == isoparse(
            SAMPLE_API_OUTPUT_JSON["data"]["created_at"]
        )
