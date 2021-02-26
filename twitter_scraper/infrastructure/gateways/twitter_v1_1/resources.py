import logging
from urllib.parse import urljoin

import requests
from requests import RequestException
from requests_oauthlib import OAuth1

from twitter_scraper.infrastructure.decorators import RateLimitDecorator
from twitter_scraper.infrastructure.gateways.twitter_v1_1.exceptions import (
    TwitterBaseError,
    TwitterInvalidFilters,
    TwitterRateLimit,
)
from twitter_scraper.infrastructure.gateways.twitter_v1_1.responses import (
    BaseSearchTweetsResponse,
)
from twitter_scraper.infrastructure.services import RequestPaginator

logger = logging.getLogger(__name__)


class SearchTweetsResource:
    def __init__(self, config, response_class=None):
        self.config = config
        self.max_limit = config.max_limit
        self.response_class = response_class or BaseSearchTweetsResponse
        self.valid_filters = {"hashtag": "#{value}", "username": "from:{value}"}
        self._request_url = urljoin(self.config.base_url, "search/tweets.json")
        self._first_payload = {}
        self.paginator = RequestPaginator(
            request_func=self._first_request,
            iter_objects_func=self._iter_response_objects,
            has_next_page_func=self._has_next_page,
            next_page_request_func=self._next_page_request,
        )

    @property
    def session_auth(self):
        return OAuth1(
            self.config.consumer_key,
            client_secret=self.config.consumer_secret,
            resource_owner_key=self.config.access_token,
            resource_owner_secret=self.config.access_token_secret,
            decoding=None,
        )

    def _get_valid_query_param(self, **query_params):
        _valid_filters = filter(
            lambda key_value: key_value[1] is not None and key_value[0] in self.valid_filters, query_params.items()
        )
        _valid_filters = list(_valid_filters)
        if len(_valid_filters) != 1:
            msg = "Filter must be only one of {} and its value should not be None".format(
                ",".join(self.valid_filters.keys())
            )
            raise TwitterInvalidFilters(msg)
        return _valid_filters[0]

    def _format_query_data(self, key, value):
        return self.valid_filters[key].format(value=value)

    def _build_query_data(self, **query_params):
        query_param = self._get_valid_query_param(**query_params)
        return self._format_query_data(*query_param)

    def _build_request_data(self, include_entities=1, result_type="recent", limit=30, **query_params):
        query_params = {
            "q": self._build_query_data(**query_params),
            "include_entities": include_entities,
            "result_type": result_type,
        }
        if limit:
            query_params["count"] = min(limit, self.max_limit)
        return query_params

    def _first_request(self):
        return self._request(url=self._request_url, payload=self._first_payload)

    def _iter_response_objects(self, response):
        return response.iter_objects()

    def _has_next_page(self, response):
        return response.has_next_page

    def _next_page_request(self, prev_response):
        payload = prev_response.get_next_page_params(limit=self.max_limit)
        return self._request(url=self._request_url, payload=payload)

    def _request(self, url, payload, auth=None, response_class=None, method="GET", **kwargs):
        auth = auth or self.session_auth
        response_class = response_class or self.response_class
        try:
            _response = requests.request(method=method, url=url, params=payload, auth=auth, **kwargs)
            response = response_class(response=_response)
            response.validate(raise_exception=True)
        except TwitterRateLimit as exc:
            raise exc
        except (RequestException, TwitterBaseError) as exc:
            logger.exception(exc)
            response = response_class(response=requests.Response())

        return response

    @RateLimitDecorator(on_exception=TwitterRateLimit, wait_period=15 * 60)
    def get(self, limit=30, **params):
        self._first_payload = self._build_request_data(limit=limit, **params)
        self.paginator(max_items=limit)
        return self.paginator.get_objects()
