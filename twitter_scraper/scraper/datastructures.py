import datetime
from typing import List

from pydantic import BaseModel


class TweetAccountData(BaseModel):
    fullname: str
    username: str
    twitter_id: int


class TweetHashtagData(BaseModel):
    name: str


class TweetData(BaseModel):
    tweet_id: int
    account: TweetAccountData
    created_at: datetime.datetime
    hashtags: List[TweetHashtagData]
    like_count: int
    reply_count: int
    retweet_count: int
    text: str
