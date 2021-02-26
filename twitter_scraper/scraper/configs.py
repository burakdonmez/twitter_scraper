from pydantic import BaseSettings

from twitter_scraper.infrastructure.gateways.enums import SearchTweetsAPIType


class SearchTweetsApiConfig(BaseSettings):
    client_type: SearchTweetsAPIType
    live: bool = True
    cache_timeout: int = 10

    class Config:
        env_prefix = "SEARCH_TWEETS_API_"
