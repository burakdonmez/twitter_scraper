from django.db import models


class TweetAccount(models.Model):
    fullname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    twitter_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Twitter Id: {self.twitter_id} Username: {self.username}"


class TweetHashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Tweet(models.Model):
    tweet_id = models.PositiveIntegerField(unique=True)
    account = models.ForeignKey(TweetAccount, related_name="tweets", on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    hashtags = models.ManyToManyField(TweetHashtag, related_name="tweets", blank=True)
    like_count = models.PositiveIntegerField()
    reply_count = models.PositiveIntegerField()
    retweet_count = models.PositiveIntegerField()
    text = models.TextField(max_length=280)

    class Meta:
        ordering = ("-tweet_id",)

    def __str__(self):
        return f"Tweet Id: {self.tweet_id} Text: {self.text[:25]}"
