from rest_framework.generics import ListAPIView

from twitter_scraper.scraper.apps import use_cases
from twitter_scraper.scraper.paginators import TweetListPaginator
from twitter_scraper.scraper.serializers import TweetSerializer


class TweetsByHashTagView(ListAPIView):
    serializer_class = TweetSerializer
    pagination_class = TweetListPaginator

    def get_queryset(self):
        limit = self.paginator.get_limit(request=self.request)
        return use_cases.list_tweets_by_hashtag(hashtag=self.kwargs["hashtag"], limit=limit)


class TweetsByUsernameView(ListAPIView):
    serializer_class = TweetSerializer
    pagination_class = TweetListPaginator

    def get_queryset(self):
        limit = self.paginator.get_limit(request=self.request)
        return use_cases.list_tweets_by_username(username=self.kwargs["username"], limit=limit)
