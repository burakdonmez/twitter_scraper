from pydantic import BaseSettings, HttpUrl


class SearchTweetsConfig(BaseSettings):
    base_url: HttpUrl = "https://api.twitter.com/1.1"
    max_limit: int = 100
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str

    class Config:
        env_prefix = "search_tweets_api_v1_1_"
