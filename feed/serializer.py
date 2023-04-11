from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from DjangoApp import settings
from feed.models import Feed, Comments
from users.models import Profile
from users.serializer import ProfileSerializer


class CommentatorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField("get_avatar", required=False, read_only=True)

    class Meta:
        model = Profile
        # fields = "__all__"
        fields = ["id", "avatar", "user", "following", "followedby", "bio", "followedby_count", "follow_count",
                  'my_posts_count']
        depth = 1

    @staticmethod
    def get_avatar(obj):
        if obj.avatar:
            base_url = settings.BASE_URL
            return base_url + obj.avatar.url
        else:
            return None


class CommentsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class FeedsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = "__all__"


class CommentsSerializer(serializers.ModelSerializer):
    commentator = CommentatorSerializer(required=False, read_only=True)
    reply_count = SerializerMethodField()
    like_count = serializers.ReadOnlyField(required=False, read_only=True)

    class Meta:
        model = Comments
        fields = "__all__"
        depth = 1

    def get_fields(self):
        fields = super(CommentsSerializer, self).get_fields()
        fields['subcomments'] = CommentsSerializer(many=True)
        return fields

    @staticmethod
    def get_reply_count(obj):
        if obj.is_parent:
            return obj.children().count()
        return obj.subcomments.count()

    """
    A another way to get replies
    @staticmethod
    def get_parent(obj):
        if obj.parent is not None:
            return CommentsSerializer(obj.parent).data
        else:
            return None
    """


class FeedSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False, read_only=True)

    num_likes = serializers.ReadOnlyField(read_only=True, required=False)
    num_replies = serializers.ReadOnlyField(read_only=True, required=False)
    num_saves = serializers.ReadOnlyField(read_only=True, required=False)
    replies = serializers.SerializerMethodField(read_only=True)
    feed_image = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Feed
        fields = "__all__"
        depth = 2

    """"ATTENTION!"""

    @staticmethod
    def get_replies(obj):
        return CommentsSerializer(obj.replies, many=True).data

    @staticmethod
    def get_feed_image(obj):
        if obj.feed_image:
            return settings.BASE_URL + obj.feed_image.url
        else:
            return None

    """""
    # ANOTHER WAY TO ADD THE BASE URL
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.feed_image:
            representation['feed_image'] = settings.BASE_URL + representation['feed_image']
        return representation
    """""
