from django.db.models import Q, Count
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from feed.models import Feed, Comments
from feed.serializer import FeedsPostSerializer, CommentsPostSerializer, FeedSerializer, CommentsSerializer
from topics.models import Topics
from users.models import Profile
from notifications.models import Notifications


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def get_comments(request, pk):
    if request.method == 'GET':
        comments = Comments.objects.filter(post=pk).annotate(num_liking=Count("liking"))
        comment = CommentsSerializer(comments, many=True)
        return Response(comment.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def get_feeds(request):
    moi = request.user
    current_profile = Profile.objects.get(user_id=request.user.id)
    followedby = current_profile.following.all()
    followers = [i.user.id for i in followedby]
    followers.append(moi.id)
    query = request.GET.get('query') if request.GET.get('query') is not None else ''

    if request.method == 'GET':
        try:
            cons = list(Feed.objects.filter(profile__user_id__in=followers).filter(
                Q(topic__name=query) |
                Q(title__contains=query) |
                Q(content__contains=query) |
                Q(title__exact=query)
            ).order_by('-posted'))[:3]

            recent_cons = Feed.objects.filter(
                Q(topic__name=query) |
                Q(title__contains=query) |
                Q(content__contains=query) |
                Q(title__exact=query)
            ).order_by('-posted')

            top_cons = Feed.objects.filter(
                Q(topic__name=query) |
                Q(title__contains=query) |
                Q(content__contains=query) |
                Q(title__exact=query)
            ).order_by('-views', '-posted')

            """Adding recent top feed to the feed list"""
            index = 0
            for con in recent_cons:
                if con not in cons:
                    cons.insert(index, con)
                    index += 1

            for con in top_cons:
                if con not in cons:
                    cons.append(con)

            serializer = FeedSerializer(cons, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)

    if request.method == 'POST':
        try:
            serializer = FeedsPostSerializer(data=request.data, many=False)
            if serializer.is_valid():
                serializer.save()

                """To send a Notification when a following profile posts"""
                for follower in followedby.all():
                    Notifications.objects.create(
                        from_profile=current_profile,
                        to_profile=follower,
                        notification_type='new_post',
                        # new_post=Feed.objects.get(profile__feed=current_profile),
                        content="has recently has posted a new article"
                    )
                return Response(serializer.data)
            return Response(serializer.errors)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def get_one_feed(request, pk):
    current_profile = Profile.objects.get(user_id=request.user.id)
    feed = Feed.objects.get(id=pk)

    if request.method == 'GET':
        try:
            feed.views += 1
            feed.save()
            serializer = FeedSerializer(feed, many=False)

            recent_posts = Feed.objects.filter(profile_id=feed.profile_id).order_by('-id').exclude(id=feed.id)[:3]
            recent_p_seriliazer = FeedSerializer(recent_posts, many=True)

            return Response({"data": serializer.data, "recent_posts": recent_p_seriliazer.data})
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)

    if request.method == "POST":  # to reply
        try:
            serializer = CommentsPostSerializer(data=request.data, many=False)
            if serializer.is_valid():
                serializer.save()
                # define it here!
                if request.data['parent'] is not None:
                    the_profile_to = request.data['commentator']
                else:
                    the_profile_to = feed.profile
                # print(the_profile_to)
                if the_profile_to == current_profile:
                    the_profile_to = None
                if the_profile_to is not None:
                    Notifications.objects.create(
                        from_profile=current_profile,
                        to_profile=the_profile_to,
                        notification_type='new_comment',
                        new_post=feed,
                        # new_comment=Comments.objects.get(commentator=current_profile, post=feed).last(),
                        content="has replied your post:".format(feed.title)
                    )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def edit_my_posts(request, pk):
    feed = Feed.objects.get(id=pk, profile__user_id=request.user.id)
    if request.method == "PATCH":
        try:
            serializer = FeedsPostSerializer(feed, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)

    if request.method == "DELETE":
        try:
            feed.delete()
            return Response(
                {"message": "You have successfully deleted your devco account and hope you will return soon",
                 "status": status.HTTP_204_NO_CONTENT})
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feed_by_topic(request, pk):
    if request.method == 'GET':
        try:
            topic = Topics.objects.get(name=pk)
            feed = Feed.objects.filter(topic=topic)
            serializer = FeedSerializer(feed, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_one_feed(request, pk):
    current_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        try:
            likes_post = get_object_or_404(Feed, id=pk)
            if likes_post.likes.filter(user_id=request.user.id).exists():
                likes_post.likes.remove(current_profile)
                likes_post.save()
                return Response("unliked")

            else:
                likes_post.likes.add(current_profile)
                likes_post.save()
                return Response("liked")
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_one_feed(request, pk):
    if request.method == "POST":
        try:
            current_profile = Profile.objects.get(user=request.user)
            saves_post = get_object_or_404(Feed, id=pk)
            if saves_post.saves.filter(user_id=request.user.id).exists():
                saves_post.saves.remove(current_profile)
                saves_post.save()
                return Response("unsaved")

            else:
                saves_post.saves.add(current_profile)
                saves_post.save()
                return Response("liked")
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_trending_feed(request):
    if request.method == 'GET':
        try:
            feed = Feed.objects.annotate(Count('views')).order_by('-views')[:8]
            serializer = FeedSerializer(feed, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_comments(request, pk):
    current_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        try:
            like_comment = get_object_or_404(Comments, id=pk)
            if like_comment.liking.filter(user_id=request.user.id).exists():
                like_comment.liking.remove(current_profile)
                like_comment.save()
                return Response("unliked")

            else:
                like_comment.liking.add(current_profile)
                like_comment.save()
                return Response("liked")
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)
