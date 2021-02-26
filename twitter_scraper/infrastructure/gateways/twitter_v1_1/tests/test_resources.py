from unittest import mock

import requests
import vcr
from django.test import TestCase, override_settings
from requests_oauthlib import OAuth1

from twitter_scraper.infrastructure.gateways.twitter_v1_1.exceptions import (
    TwitterInvalidFilters,
)
from twitter_scraper.infrastructure.gateways.twitter_v1_1.resources import (
    SearchTweetsResource,
)
from twitter_scraper.infrastructure.gateways.twitter_v1_1.responses import (
    BaseSearchTweetsResponse,
)

my_vcr = vcr.VCR(
    cassette_library_dir="fixtures/cassettes/search_tweets_v_1_1/",
    record_mode="once",
    decode_compressed_response=True,
)

test_settings = override_settings(
    TWEET_LISTING_DEFAULT_LIMIT=30,
)


class SearchTweetsResourceTestCase(TestCase):
    def setUp(self):
        class DummyConfig:
            base_url = "https://api.twitter.com/1.1"
            max_limit = 100
            consumer_key = "dummy"
            consumer_secret = "dummy"
            access_token = "dummy"
            access_token_secret = "dummy"

        class DummyResponse:
            def get_objects(self):
                return []

            def iter_objects(self):
                return iter(self.get_objects())

            def get_next_page_params(self, limit):
                return {}

            @property
            def has_next_page(self):
                return False

        self.dummy_config = DummyConfig()
        self.resource = SearchTweetsResource(config=self.dummy_config)
        self.empty_response = DummyResponse()
        self._mock_response = requests.Response()
        self._mock_response.status_code = 200

    def test_session_auth(self):
        self.assertTrue(isinstance(self.resource.session_auth, OAuth1))

    def test_get_valid_query_param_given_valid_query_params(self):
        self.resource._get_valid_query_param(hashtag="dummy")

    def test_get_valid_query_param_given_invalid_multiple_query_params(self):
        with self.assertRaises(TwitterInvalidFilters):
            self.resource._get_valid_query_param(hashtag="dummy", username="dummy")

    def test_get_valid_query_param_given_invalid_single_query_params(self):
        with self.assertRaises(TwitterInvalidFilters):
            self.resource._get_valid_query_param(dummy="dummy")

        with self.assertRaises(TwitterInvalidFilters):
            self.resource._get_valid_query_param(hashtag=None)

    def test_build_query_data(self):
        formatted_str = self.resource._build_query_data(hashtag="dummy")
        self.assertEqual(formatted_str, "#dummy")

    def test_build_request_data(self):
        query_params = {
            "hashtag": "dummy",
        }
        built_data = self.resource._build_request_data(
            include_entities=1, result_type="recent", limit=150, **query_params
        )
        expected_data = {
            "q": "#dummy",
            "include_entities": 1,
            "result_type": "recent",
            "count": self.dummy_config.max_limit,
        }
        self.assertDictEqual(expected_data, built_data)

        query_params = {
            "username": "dummy",
        }
        built_data = self.resource._build_request_data(
            include_entities=1, result_type="recent", limit=150, **query_params
        )
        expected_data = {
            "q": "from:dummy",
            "include_entities": 1,
            "result_type": "recent",
            "count": self.dummy_config.max_limit,
        }
        self.assertDictEqual(expected_data, built_data)

    @mock.patch("twitter_scraper.infrastructure.gateways.twitter_v1_1.resources.requests.request")
    def test_first_request(self, mock_request):
        mock_request.return_value = self._mock_response
        response = self.resource._first_request()
        self.assertTrue(isinstance(response, BaseSearchTweetsResponse))

    def test_iter_response_objects(self):
        objects = self.resource._iter_response_objects(response=self.empty_response)
        self.assertEqual(list(objects), [])

    def test_has_next_page(self):
        result = self.resource._has_next_page(response=self.empty_response)
        self.assertFalse(result)

    @mock.patch("twitter_scraper.infrastructure.gateways.twitter_v1_1.resources.requests.request")
    def test_next_page_request(self, mock_request):
        mock_request.return_value = self._mock_response
        response = self.resource._next_page_request(prev_response=self.empty_response)
        self.assertTrue(isinstance(response, BaseSearchTweetsResponse))

    @mock.patch("twitter_scraper.infrastructure.gateways.twitter_v1_1.resources.requests.request")
    def test_request(self, mock_request):
        mock_request.return_value = self._mock_response
        response = self.resource._request(url=self.resource._request_url, payload={})
        self.assertTrue(isinstance(response, BaseSearchTweetsResponse))

    @my_vcr.use_cassette("guido_tweets_1_object.yaml", match_on=["method", "host"])
    def test_get(self):
        expected_object = {
            "created_at": "Thu Jun 10 23:13:35 +0000 2021",
            "id": 1403128238184956000,
            "text": "dummy",
            "entities": {"hashtags": [{"name": "dummy"}, {"name": "dumm2"}]},
            "user": {"id": 15804774, "name": "GuidovanRossum", "screen_name": "gvanrossum"},
            "retweet_count": 5,
            "favorite_count": 27,
        }

        generator = self.resource.get(hashtag="dummy")
        obj = next(generator)
        self.assertDictEqual(expected_object, obj)
