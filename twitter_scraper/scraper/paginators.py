from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination


class TweetListPaginator(LimitOffsetPagination):
    default_limit = settings.TWEET_LISTING_DEFAULT_LIMIT
