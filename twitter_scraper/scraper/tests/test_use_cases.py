import collections
import datetime
from unittest import mock

import vcr
from django.test import TestCase, override_settings

from twitter_scraper.scraper.models import Tweet
from twitter_scraper.scraper.use_cases import (
    create_tweets,
    fetch_tweets,
    populate_tweets,
    validate_tweets,
)

my_vcr = vcr.VCR(
    cassette_library_dir="fixtures/cassettes/search_tweets_v_1_1/",
    record_mode="once",
    decode_compressed_response=True,
)

test_settings = override_settings(
    TWEET_LISTING_DEFAULT_LIMIT=30,
)


class DummyTestDataMixin:
    dummy_date = datetime.datetime.now()
    dummy_valid_data_1 = {
        "created_at": dummy_date,
        "hashtags": [{"name": "dummy"}],
        "like_count": 27,
        "tweet_id": 1403128238184955906,
        "reply_count": 0,
        "retweet_count": 5,
        "text": "dummy",
        "account": {
            "twitter_id": 15804774,
            "fullname": "Guido van Rossum",
            "username": "gvanrossum",
        },
    }

    dummy_valid_data_2 = {
        "created_at": dummy_date,
        "hashtags": [{"name": "dummy2"}],
        "like_count": 27,
        "tweet_id": 1403128238184955907,
        "reply_count": 0,
        "retweet_count": 5,
        "text": "dummy2",
        "account": {
            "twitter_id": 15804774,
            "fullname": "Guido van Rossum",
            "username": "gvanrossum",
        },
    }

    dummy_invalid_data_1 = {}


class FetchTweetsTestCase(TestCase):
    def setUp(self):
        self.dummy_result = ["dummy result 1", "dummy result 2"]

        class DummyResource:
            result = self.dummy_result

            def get(self):
                return self.result

        self.dummy_resource = DummyResource()

    @test_settings
    def test_fetch_tweets(self):
        decorated_resource = fetch_tweets(resource=self.dummy_resource)
        self.assertListEqual(list(decorated_resource()), self.dummy_result)


class ValidateTweetsTestCase(TestCase, DummyTestDataMixin):
    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_raw_objects_given_multiple_valid_objects(self, mock_logger):
        dummy_raw_objs = [self.dummy_valid_data_1, self.dummy_valid_data_2]
        generator = validate_tweets(raw_objs=dummy_raw_objs)
        collections.deque(generator, maxlen=0)
        self.assertFalse(mock_logger.debug.called)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_raw_objects_given_single_valid_object(self, mock_logger):
        dummy_raw_obj = self.dummy_valid_data_1
        generator = validate_tweets(raw_objs=dummy_raw_obj)
        collections.deque(generator, maxlen=0)
        self.assertFalse(mock_logger.debug.called)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_raw_objects_given_single_invalid_object(self, mock_logger):
        dummy_raw_obj = self.dummy_invalid_data_1
        generator = validate_tweets(raw_objs=dummy_raw_obj)
        collections.deque(generator, maxlen=0)
        self.assertTrue(mock_logger.debug.called)


class CreateTweetsTestCase(TestCase, DummyTestDataMixin):
    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_multiple_valid_objects(self, mock_logger):
        dummy_objs = [self.dummy_valid_data_1, self.dummy_valid_data_2]
        generator = create_tweets(validated_objs=dummy_objs)
        collections.deque(generator, maxlen=0)
        self.assertFalse(mock_logger.debug.called)
        self.assertFalse(mock_logger.exception.called)

        dummy_objs_ids = [i["tweet_id"] for i in dummy_objs]
        count = Tweet.objects.filter(tweet_id__in=dummy_objs_ids).count()
        expected_count = len(dummy_objs)
        self.assertEqual(count, expected_count)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_single_valid_object(self, mock_logger):
        dummy_obj = self.dummy_valid_data_1
        generator = create_tweets(validated_objs=dummy_obj)
        collections.deque(generator, maxlen=0)
        self.assertFalse(mock_logger.debug.called)
        self.assertFalse(mock_logger.exception.called)

        Tweet.objects.get(tweet_id=dummy_obj["tweet_id"])

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_single_invalid_object(self, mock_logger):
        dummy_obj = self.dummy_invalid_data_1
        generator = create_tweets(validated_objs=dummy_obj)
        collections.deque(generator, maxlen=0)
        self.assertTrue(mock_logger.exception.called)

        self.assertEqual(Tweet.objects.all().count(), 0)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_already_exists(self, mock_logger):
        dummy_objs = [self.dummy_valid_data_1, self.dummy_valid_data_1]
        generator = create_tweets(validated_objs=dummy_objs)
        collections.deque(generator, maxlen=0)
        self.assertTrue(mock_logger.debug.called)
        self.assertFalse(mock_logger.exception.called)

        Tweet.objects.get(tweet_id=dummy_objs[0]["tweet_id"])


class PopulateTweetsTestCase(TestCase, DummyTestDataMixin):
    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_multiple_valid_objects(self, mock_logger):
        raw_objs = [self.dummy_valid_data_1, self.dummy_valid_data_2]
        populate_tweets(raw_objs=raw_objs)

        raw_objs_ids = [i["tweet_id"] for i in raw_objs]
        count = Tweet.objects.filter(tweet_id__in=raw_objs_ids).count()
        expected_count = len(raw_objs)
        self.assertEqual(count, expected_count)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_single_valid_object(self, mock_logger):
        raw_obj = self.dummy_valid_data_1
        populate_tweets(raw_objs=raw_obj)

        Tweet.objects.get(tweet_id=raw_obj["tweet_id"])

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_single_invalid_object(self, mock_logger):
        raw_obj = self.dummy_invalid_data_1
        populate_tweets(raw_objs=raw_obj)

        self.assertEqual(Tweet.objects.all().count(), 0)

    @mock.patch("twitter_scraper.scraper.use_cases.logger")
    def test_validated_objects_given_already_exists(self, mock_logger):
        raw_objs = [self.dummy_valid_data_1, self.dummy_valid_data_1]
        populate_tweets(raw_objs=raw_objs)
        Tweet.objects.get(tweet_id=raw_objs[0]["tweet_id"])
