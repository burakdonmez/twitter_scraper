from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthcheckConfig(AppConfig):
    name = "healthcheck"

    def ready(self):
        from twitter_scraper.healthcheck.backends import TwitterApiBackend

        plugin_dir.register(TwitterApiBackend)
