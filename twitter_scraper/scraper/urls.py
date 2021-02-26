from django.urls import path

from twitter_scraper.scraper.views import TweetsByHashTagView, TweetsByUsernameView

urlpatterns = [
    path("hashtags/<hashtag>/", TweetsByHashTagView.as_view(), name="tweets_by_hashtag"),
    path("users/<username>/", TweetsByUsernameView.as_view(), name="tweets_by_users"),
]
