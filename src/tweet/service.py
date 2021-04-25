import requests
from requests import Response
from logging import Logger
from os import getenv
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from dateutil.parser import isoparse

logger = Logger(__name__)

@dataclass
class Tweet:
    """Data class to represent a tweet as consumed by Espresso.
    """

    text: str
    id: str
    created_at: str
    created_date: datetime = field(init=False)
    author_id: str
    conversation_id: str
    in_reply_to_user_id: str = None

    def __post_init__(self):
        self.created_date = isoparse(self.created_at)

class TwitterService:
    """Methods for interacting with the Twitter API (un-rolling tweets, etc.)
    """

    def __init__(self):
        self.bearer_token = getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            logger.warning("Twitter API credentials not found in environment variables - Twitter features will be disabled.")
    

    def make_get_request(self, url: str, params: dict) -> Optional[Response]:
        """Makes a GET request to the Twitter API.

        Args:
            url: The resource to access (i.e. /tweets)
            params: A dictionary of query params to append to the URL.
        
        Returns:
            A requests.Response object, or None.
        """
        if not self.bearer_token:
            return None
        response = requests.get(
            f'https://api.twitter.com/2{url}',
            params=params,
            headers={
                'Authorization': f'Bearer {self.bearer_token}'
            }
        )
        return response

    def get_tweet_by_id(self, id: str) -> Optional[Tweet]:
        """Fetches a tweet by tweet ID. Uses the /tweets resource.
        """

        params = {
            'tweet.fields': 'author_id,conversation_id,created_at',
            'expansions': 'author_id,in_reply_to_user_id',
            'user.fields': 'name,username'
        }

        response = self.make_get_request(f'/tweets/{id}', params=params)
        if response:
            if response.status_code != 200:
                logger.warning(f"Issue fetching tweet from the Twitter API: {response.text}")
            response_json = response.json()
            return Tweet(**response_json['data'])
        return None

    def expand_tweet_thread(self, tweet: Tweet) -> List[Tweet]:
        """Finds all self-replies to a given tweet, and returns a list of
        all replies (including the original tweet). Note this is not available
        if the tweet is older than 7 days.

        More:
            Twitter: Conversation IDs
            https://developer.twitter.com/en/docs/twitter-api/conversation-id
        """

        query = f'conversation_id: {tweet.conversation_id} from: {tweet.author_id} to: {tweet.author_id}'
        response = self.make_get_request(
            f'/tweets/search/recent',
            params={
                'query': query,
                'tweet.fields': 'in_reply_to_user_id,author_id,created_at,conversation_id'
            }
        )
        if response:
            if response.status_code != 200:
                logger.warning(f"Issue fetching thread from the Twitter API: {response.text}")
                return [tweet]
            response_data = response.json()['data']
            all_tweets_in_thread = [tweet]
            for tweet_data in response_data:
                all_tweets_in_thread.append(Tweet(**tweet_data))
                all_tweets_in_thread.sort(key=lambda x: x.created_date)

            return all_tweets_in_thread

        return [tweet]


    