from rest_framework import generics
from rest_framework.viewsets import ViewSet
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer
from rest_framework.viewsets import ViewSet


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentViewSet(ViewSet):
    def get_comments_by_post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        comments = Comment.objects.filter(post_id=post_id)

