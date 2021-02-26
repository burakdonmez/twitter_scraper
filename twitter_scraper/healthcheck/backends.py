from health_check.backends import BaseHealthCheckBackend
from memoize import memoize

from twitter_scraper.infrastructure.exceptions import Error
from twitter_scraper.scraper.apps import use_cases


class TwitterApiBackend(BaseHealthCheckBackend):
    #: The status endpoints will respond with a 200 status code
    #: even if the check errors.
    critical_service = True

    @staticmethod
    @memoize(timeout=10)
    def _check_api_status():
        test_hashtag = "test"
        test_username = "jack"
        use_cases.fetch_api_tweets(hashtag=test_hashtag, limit=1)
        use_cases.fetch_api_tweets(username=test_username, limit=1)

    def check_status(self):
        try:
            self._check_api_status()
        except Error as exc:
            self.add_error(exc, exc)

    def identifier(self):
        return self.__class__.__name__
