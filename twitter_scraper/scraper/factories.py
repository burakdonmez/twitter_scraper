from twitter_scraper.infrastructure.factories import ObjectFactory


class SearchTweetsAPIFactory(ObjectFactory):
    pass


def build_search_tweets_api_v1_1(config=None):
    from twitter_scraper.infrastructure.gateways.twitter_v1_1.configs import (
        SearchTweetsConfig,
    )
    from twitter_scraper.infrastructure.gateways.twitter_v1_1.resources import (
        SearchTweetsResource,
    )
    from twitter_scraper.infrastructure.gateways.twitter_v1_1.responses import (
        SearchTweetsResponse,
    )

    config = config or SearchTweetsConfig()
    return SearchTweetsResource(config=config, response_class=SearchTweetsResponse)


def build_tweet_api_fetcher():
    from twitter_scraper.scraper.apps import search_tweets_api_factory
    from twitter_scraper.scraper.configs import SearchTweetsApiConfig
    from twitter_scraper.scraper.use_cases import fetch_tweets

    config = SearchTweetsApiConfig()
    api_resource = search_tweets_api_factory.create(key=config.client_type)
    return fetch_tweets(resource=api_resource, live=config.live, cache_timeout=config.cache_timeout)


def build_tweet_listing(fetch_data_use_case, query_func):
    from twitter_scraper.scraper.use_cases import ListingTweets, populate_tweets

    return ListingTweets(
        fetch_data_use_case=fetch_data_use_case, populate_use_case=populate_tweets, query_func=query_func
    )
