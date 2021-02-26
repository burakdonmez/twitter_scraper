from types import SimpleNamespace

from django.apps import AppConfig

from twitter_scraper.infrastructure.gateways.enums import SearchTweetsAPIType
from twitter_scraper.scraper.factories import (
    SearchTweetsAPIFactory,
    build_search_tweets_api_v1_1,
    build_tweet_api_fetcher,
    build_tweet_listing,
)
from twitter_scraper.scraper.queries import filter_by_hashtag, filter_by_username


class ScraperConfig(AppConfig):
    name = "scraper"


search_tweets_api_factory = SearchTweetsAPIFactory()
search_tweets_api_factory.register_builder(key=SearchTweetsAPIType.v1_1, builder=build_search_tweets_api_v1_1)

use_cases = SimpleNamespace()

use_cases.fetch_api_tweets = build_tweet_api_fetcher()
use_cases.list_tweets_by_username = build_tweet_listing(
    fetch_data_use_case=use_cases.fetch_api_tweets,
    query_func=filter_by_username,
)

use_cases.list_tweets_by_hashtag = build_tweet_listing(
    fetch_data_use_case=use_cases.fetch_api_tweets,
    query_func=filter_by_hashtag,
)
