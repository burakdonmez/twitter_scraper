from twitter_scraper.scraper.models import Tweet


def filter_by_hashtag(hashtag, **params):
    return Tweet.objects.filter(hashtags__name__iexact=hashtag).prefetch_related("hashtags").distinct()


def filter_by_username(username, **params):
    return Tweet.objects.filter(account__username=username).select_related("account").distinct()
