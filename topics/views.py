from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from feed.models import Feed
from feed.serializer import FeedSerializer
from topics.models import Topics
from topics.serializers import TopicsCountSerializer, TopicsSerializer


# username: alphaoumardev
# password: Wanglishi200@

# Questions
# city: Nanjing
# university: NUIST
# mom: Fatoumata Binta
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def get_topics(request):
    if request.method == 'GET':
        topic = Topics.objects.all().annotate(post_count=Count("topic")).order_by('-post_count')  # and count
        serializer = TopicsCountSerializer(topic, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = TopicsSerializer(data=request.data, many=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def get_one_topic(request, pk):
    if request.method == 'GET':
        topic = Topics.objects.get(id=pk)
        feed = Feed.objects.filter(topic_id=topic)

        count = feed.count()
        serializer = FeedSerializer(feed, many=True)
        return Response({"data": serializer.data, "count": count})
