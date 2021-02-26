from rest_framework import serializers

from twitter_scraper.scraper.models import Tweet, TweetAccount, TweetHashtag


class TweetAccountSerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()
    id = serializers.IntegerField(source="twitter_id")

    class Meta:
        model = TweetAccount
        fields = ("fullname", "href", "id")

    def get_href(self, instance):
        return f"/{instance.username}"


class TweetHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetHashtag
        fields = ("name",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return f"#{data['name']}"


class TweetSerializer(serializers.ModelSerializer):
    account = TweetAccountSerializer()
    date = serializers.DateTimeField(source="created_at", format="%l:%M %p - %d %b %Y")
    hashtags = TweetHashtagSerializer(many=True)
    likes = serializers.IntegerField(source="like_count")
    replies = serializers.IntegerField(source="reply_count")
    retweets = serializers.IntegerField(source="retweet_count")

    class Meta:
        model = Tweet
        fields = ("account", "date", "hashtags", "likes", "replies", "retweets", "text")
