import requests
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
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
        tags=['posts'],
        security=[{'Bearer': []}]

    )
    def post_delete(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if user.status_code != 200:
            return Response(user.json(), user.status_code)

        post_id = request.data.get('post_id')
        post = Post.objects.filter(id=post_id).first()
        if post:
            if post.author == user.json().get('id'):
                post.delete()
                return Response({'detail': "post deleted"}, status.HTTP_200_OK)
            return Response({"detail": "u cant delete this post"}, status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Post not found"}, status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Get all posts",
        operation_summary="get posts",
        manual_parameters=[
            openapi.Parameter('page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('title', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter('category', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
        ],
        responses={200: PostSerializer()},
        tags=['get-posts']
    )
    def get_posts(self, request, *args, **kwargs):
        size = request.GET.get('size', 5)

        posts = Post.objects.all()
        if not (isinstance(size, int) and size > 0):
            size = 5

        title = request.GET.get('title', None)
        if title:
            posts = posts.filter(title__contains=title)

        category = request.GET.get('category', None)
        if category:
            posts = posts.filter(category=category)

        paginator = PageNumberPagination()
        paginator.page_size = size
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create your post",
        operation_summary="Create post",
        responses={200: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER),

            },
            required=['title', 'description', ]
        ),
        tags=['posts']

    )
    def create_post(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if user.status_code != 200:
            return Response(user.json(), user.status_code)

        serializer = PostSerializer(data=request.data, context={"user_id": user.json().get('id')})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        obj = Post.objects.filter(id=pk).first()

        if not obj:
            return Response({"error": "Post not found"}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(obj)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if user.status_code != 200:
            return Response(user.json(), status=user.status_code)

        post = Post.objects.filter(author=user.json().get('id')).first()
        if not post:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        like_obj = Like.objects.filter(post=post, author=user.json().get('id')).first()
        if like_obj:
            like_obj.delete()
            post.like_count -= 1
            post.save(update_fields=['like_count'])
            return Response({"detail": "Unliked"}, status.HTTP_200_OK)

        like_obj = Like.objects.create(post=post, author=user.json().get('id'))
        like_obj.save()
        post.like_count += 1
        post.save(update_fields=['like_count'])
        return Response({"detail": "Liked"}, status.HTTP_200_OK)

    def check_authentication(self, access_token):
        data = self.get_one_time_token()
        if data.status_code != 200:
            return data
        response = requests.post('http://134.122.76.27:8118/api/v1/me/', data=data,
                                 headers={"Authorization": access_token})
        return response

    def get_one_time_token(self):
        response = requests.post(url='http://134.122.76.27:8114/api/v1/login/',
                                 data={"secret_key": settings.SECRET_SERVICE_KEY,
                                       "service_id": settings.SECRET_SERVICE_ID,
                                       "service_name": settings.SECRET_SERVICE_NAME})
        return response
