import datetime
import functools
import logging
from urllib.parse import parse_qs

from twitter_scraper.infrastructure import utils
from twitter_scraper.infrastructure.gateways.mixins import ValidateResponseMixin
from twitter_scraper.infrastructure.gateways.twitter_v1_1 import exceptions
from twitter_scraper.infrastructure.gateways.twitter_v1_1.exceptions import (
    TwitterUnknown,
)

logger = logging.getLogger(__name__)


class BaseSearchTweetsResponse(ValidateResponseMixin):
    errors = exceptions.ERRORS

    def __init__(self, response):
        self._response = response
        self.status_code = self._response.status_code

    def _is_response_ok(self):
        return self._response.ok

    def _get_error(self):
        return self.errors.get(self.status_code, TwitterUnknown)

    @functools.cached_property
    def dict_content(self):
        if not self._response.content:
            return {}
        return self._response.json()

    def get_objects(self):
        return utils.get_list(self.dict_content, ["statuses"])

    def iter_objects(self):
        return iter(self.get_objects())

    def get_next_page_params(self, limit):
        if "next_results" not in self.dict_content["search_metadata"]:
            return {}

        qs = self.dict_content["search_metadata"]["next_results"]
        qs = qs.replace("?", "", 1)
        qs = parse_qs(qs)
        next_page_params = {
            "max_id": qs["max_id"][0],
            "q": qs["q"][0],
            "count": limit,
            "result_type": qs["result_type"][0],
            "include_entities": qs["include_entities"][0],
        }
        return next_page_params

    @property
    def has_next_page(self):
        return "search_metadata" in self.dict_content and "next_results" in self.dict_content["search_metadata"]


class SearchTweetsResponse(BaseSearchTweetsResponse):
    @staticmethod
    def _parse_account(dict_):
        account = {
            "fullname": dict_["name"],
            "username": dict_["screen_name"],
            "twitter_id": dict_["id"],
        }
        return account

    @staticmethod
    def _parse_hashtags(list_):
        hashtags = [{"name": hashtag_data["text"]} for hashtag_data in list_]
        return hashtags

    @staticmethod
    def _parse_created_at(date):
        return datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %z %Y")

    def iter_objects(self):
        for dict_ in super(SearchTweetsResponse, self).iter_objects():
            try:
                formatted_dict = {
                    "tweet_id": int(dict_["id"]),
                    "account": self._parse_account(dict_=dict_["user"]),
                    "created_at": self._parse_created_at(dict_["created_at"]),
                    "hashtags": self._parse_hashtags(list_=utils.get_list(dict_["entities"], ["hashtags"])),
                    "like_count": int(dict_["favorite_count"]),
                    "reply_count": 0,
                    "retweet_count": int(dict_["retweet_count"]),
                    "text": dict_["text"],
                }
            except (KeyError, ValueError) as exc:
                logger.exception(exc)
                continue

            yield formatted_dict
