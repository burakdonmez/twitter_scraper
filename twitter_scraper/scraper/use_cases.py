import collections
import logging
import traceback

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import Error as DjangoDbBaseError
from pydantic import ValidationError as PydanticValidationError

from twitter_scraper.infrastructure.decorators import memoize_generator
from twitter_scraper.infrastructure.utils import enforce_sequence
from twitter_scraper.scraper.datastructures import TweetData
from twitter_scraper.scraper.services import create_tweet_from_dict

logger = logging.getLogger(__name__)


class ListingTweets:
    def __init__(self, fetch_data_use_case, populate_use_case, query_func):
        self.fetch_raw_tweets = fetch_data_use_case
        self.populate_tweets = populate_use_case
        self.query_tweets = query_func

    def __call__(self, **params):
        raw_objs = self.fetch_raw_tweets(**params)
        self.populate_tweets(raw_objs)
        return self.query_tweets(**params)


def fetch_tweets(resource, live=True, cache_timeout=10):
    @memoize_generator(unless=lambda: live, timeout=cache_timeout)
    def _fetcher(**params):
        return resource.get(**params)

    return _fetcher


def validate_tweets(raw_objs):
    raw_objs = enforce_sequence(raw_objs)
    for raw_obj in raw_objs:
        try:
            validated_obj = TweetData.parse_obj(raw_obj)
            yield validated_obj.dict()
        except PydanticValidationError:
            logger.debug(traceback.format_exc())
            continue


def create_tweets(validated_objs):
    validated_objs = enforce_sequence(validated_objs)
    for validated_obj in validated_objs:
        try:
            db_obj = create_tweet_from_dict(**validated_obj)
            yield db_obj
        except DjangoValidationError:
            logger.debug(traceback.format_exc())
            continue
        except (DjangoDbBaseError, KeyError) as exc:
            logger.exception(exc)
            continue


def populate_tweets(raw_objs):
    validated_objs = validate_tweets(raw_objs=raw_objs)
    generator = create_tweets(validated_objs=validated_objs)
    collections.deque(generator, maxlen=0)
