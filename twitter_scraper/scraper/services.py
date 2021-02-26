import logging

from django.db import transaction

from twitter_scraper.scraper.models import Tweet, TweetAccount, TweetHashtag

logger = logging.getLogger(__name__)


def get_or_create_account(fullname, username, twitter_id):
    account_obj, _ = TweetAccount.objects.get_or_create(
        fullname=fullname,
        username=username,
        twitter_id=twitter_id,
    )
    return account_obj


def get_or_create_hashtag(name):
    hashtag_obj, _ = TweetHashtag.objects.get_or_create(name=name)
    return hashtag_obj


def create_tweet(tweet_id, account_obj, created_at, like_count, reply_count, retweet_count, text, hashtags=None):
    tweet_obj = Tweet(
        tweet_id=tweet_id,
        account=account_obj,
        created_at=created_at,
        like_count=like_count,
        reply_count=reply_count,
        retweet_count=retweet_count,
        text=text,
    )
    tweet_obj.full_clean(validate_unique=True)
    tweet_obj.save()
    if hashtags:
        tweet_obj.hashtags.set(hashtags)
    return tweet_obj


@transaction.atomic()
def create_tweet_from_dict(**validated_dict):
    account_dict = validated_dict.pop("account")
    account_obj = get_or_create_account(**account_dict)

    hashtags_list = validated_dict.pop("hashtags", [])
    hashtag_objs = [get_or_create_hashtag(name=hashtag["name"]) for hashtag in hashtags_list]

    return create_tweet(account_obj=account_obj, hashtags=hashtag_objs, **validated_dict)
