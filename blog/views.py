from rest_framework import generics
from rest_framework.viewsets import ViewSet
from .models import Post
from .serializers import PostSerializer
from rest_framework.viewsets import ViewSet


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
