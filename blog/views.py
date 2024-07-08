import requests
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.paginator import Paginator
from .models import Post, Like
from .serializers import PostSerializer


class PostViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="Delete your post",
        operation_summary="Delete post",
        responses={200: "post deleted"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['post_id']
        ),
        tags=['posts']

    )
    def post_delete(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if not user:
            return Response({"error": "user is not authenticated"}, status.HTTP_401_UNAUTHORIZED)
        post_id = request.data.get('post_id')
        post = Post.objects.filter(id=post_id).first()
        if post:
            if post.author == user['id']:
                post.delete()
                return Response({'detail': "post deleted"}, status.HTTP_200_OK)
            return Response({"detail": "u cant delete this post"}, status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Post not found"}, status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Get all posts",
        operation_summary="get posts",
        manual_parameters=[
            openapi.Parameter('page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY ),
            openapi.Parameter('size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('title', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter('category', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
        ],
        responses={200: PostSerializer()},
        tags=['movie']
    )
    def get_posts(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 5)

        posts = Post.objects.all()
        if not (isinstance(page, int) and page > 0):
            page = 1
        if not (isinstance(size, int) and size > 0):
            size = 5

        title = request.GET.get('title', None)
        if title:
            posts = posts.filter(title__contains=title)

        category = request.GET.get('category', None)
        if category:
            posts = posts.filter(category=category)

        paginator = Paginator(posts, size)
        post_paginator = paginator.page(page)
        return Response(data=post_paginator, status=status.HTTP_200_OK)

    def check_authentication(self, access_token):
        response = requests.get('', data=access_token)
        if response.status_code == 200:
            return response.json()
        return False

    def list(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, id=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikePostViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="Like or unlike",
        operation_summary="Like boss yo unlike boss",
        responses={200: "Liked or unliked"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['post_id']
        ),
        tags=['posts']

    )
    def like_unlike_post(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if not user:
            return Response({"error": "user is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        post = Post.objects.filter(user=user['id']).first()
        if not post:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        like_obj = Like.objects.filter(post=post, user=user['id']).first()
        if like_obj:
            like_obj.delete()
            post.like_count -= 1
            post.save(update_fields=['like_count'])
            return Response({"detail": "Unliked"}, status.HTTP_200_OK)

        like_obj = Like.objects.create(post=post, user=user['id'])
        like_obj.save()
        post.like_count += 1
        post.save(update_fields=['like_count'])
        return Response({"detail": "Liked"}, status.HTTP_200_OK)

    def check_authentication(self, access_token):
        response = requests.get('', data=access_token)
        if response.status_code == 200:
            return response.json()
        return False
