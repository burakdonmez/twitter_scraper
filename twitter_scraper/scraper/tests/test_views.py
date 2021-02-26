import vcr
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from twitter_scraper.scraper.models import Tweet

my_vcr = vcr.VCR(
    cassette_library_dir="fixtures/cassettes/search_tweets_v_1_1/",
    record_mode="once",
    decode_compressed_response=True,
)

test_settings = override_settings(
    TWEET_LISTING_DEFAULT_LIMIT=30,
)


class TweetsByHashTagViewTestCase(TestCase):
    def setUp(self):
        self.default_limit = settings.TWEET_LISTING_DEFAULT_LIMIT

    @test_settings
    @my_vcr.use_cassette("nasa_tweets_16_valid_objects_total_30_objects.yaml")
    def test_get_with_30_objects(self):
        url = reverse("tweets_by_hashtag", kwargs={"hashtag": "nasa"}) + "?format=json"
        response = self.client.get(url)
        valid_objects_count = 16
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], valid_objects_count)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), valid_objects_count)

        obj = json_response["results"][0]
        self.assertIn("account", obj)
        self.assertIn("fullname", obj["account"])
        self.assertIn("href", obj["account"])
        self.assertIn("id", obj["account"])
        self.assertIn("date", obj)
        self.assertIn("hashtags", obj)
        self.assertIn("likes", obj)
        self.assertIn("replies", obj)
        self.assertIn("retweets", obj)
        self.assertIn("text", obj)

        self.assertEqual(Tweet.objects.all().count(), self.default_limit)

    @test_settings
    @my_vcr.use_cassette("nasa_tweets_16_valid_objects_total_30_objects.yaml", match_on=["method", "host"])
    def test_get_with_limit_10_objects(self):
        limit = 10
        url = reverse("tweets_by_hashtag", kwargs={"hashtag": "nasa"}) + "?limit=10&format=json"
        response = self.client.get(url)
        valid_objects_count = 5
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], valid_objects_count)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), valid_objects_count)

        obj = json_response["results"][0]
        self.assertIn("account", obj)
        self.assertIn("fullname", obj["account"])
        self.assertIn("href", obj["account"])
        self.assertIn("id", obj["account"])
        self.assertIn("date", obj)
        self.assertIn("hashtags", obj)
        self.assertIn("likes", obj)
        self.assertIn("replies", obj)
        self.assertIn("retweets", obj)
        self.assertIn("text", obj)

        self.assertEqual(Tweet.objects.all().count(), limit)

    @test_settings
    @my_vcr.use_cassette("hashtag_tweets_empty_result.yaml")
    def test_get_with_empty_result(self):
        url = reverse("tweets_by_hashtag", kwargs={"hashtag": "asdasdsadsadasdsafasf"}) + "?format=json&"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], 0)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), 0)


class TweetsByUsernameViewTestCase(TestCase):
    def setUp(self):
        self.default_limit = settings.TWEET_LISTING_DEFAULT_LIMIT

    @test_settings
    @my_vcr.use_cassette("guido_tweets_10_objects.yaml")
    def test_get_with_30_objects(self):
        url = reverse("tweets_by_users", kwargs={"username": "gvanrossum"}) + "?format=json"
        response = self.client.get(url)
        valid_objects_count = 10
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], valid_objects_count)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), valid_objects_count)

        obj = json_response["results"][0]
        self.assertIn("account", obj)
        self.assertIn("fullname", obj["account"])
        self.assertIn("href", obj["account"])
        self.assertIn("id", obj["account"])
        self.assertIn("date", obj)
        self.assertIn("hashtags", obj)
        self.assertIn("likes", obj)
        self.assertIn("replies", obj)
        self.assertIn("retweets", obj)
        self.assertIn("text", obj)
        self.assertEqual(Tweet.objects.all().count(), valid_objects_count)

    @test_settings
    @my_vcr.use_cassette("guido_tweets_10_objects.yaml", match_on=["method", "host"])
    def test_get_with_5_objects(self):
        url = reverse("tweets_by_users", kwargs={"username": "gvanrossum"}) + "?limit=5&format=json"
        response = self.client.get(url)
        valid_objects_count = 5
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], valid_objects_count)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), valid_objects_count)

        obj = json_response["results"][0]
        self.assertIn("account", obj)
        self.assertIn("fullname", obj["account"])
        self.assertIn("href", obj["account"])
        self.assertIn("id", obj["account"])
        self.assertIn("date", obj)
        self.assertIn("hashtags", obj)
        self.assertIn("likes", obj)
        self.assertIn("replies", obj)
        self.assertIn("retweets", obj)
        self.assertIn("text", obj)
        self.assertEqual(Tweet.objects.all().count(), valid_objects_count)

    @test_settings
    @my_vcr.use_cassette("username_tweets_empty_result.yaml")
    def test_get_with_empty_result(self):
        url = reverse("tweets_by_users", kwargs={"username": "asdasdsadsadasdsafasf"}) + "?format=json&"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertEqual(json_response["count"], 0)
        self.assertEqual(json_response["next"], None)
        self.assertEqual(json_response["previous"], None)
        self.assertEqual(len(json_response["results"]), 0)
