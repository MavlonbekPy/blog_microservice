import requests
from rest_framework.decorators import api_view
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
import random


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
        operation_summary="get posts for users",
        manual_parameters=[
            openapi.Parameter('page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('title', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter('category', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
        ],
        responses={200: PostSerializer()},
        tags=['posts']
    )
    def get_posts(self, request, *args, **kwargs):
        size = request.query_params.get('size', 5)
        try:
            size = int(size)
        except ValueError:
            size = 5

        if size <= 0:
            size = 5

        posts = Post.objects.all()

        title = request.GET.get('title', None)
        if title:
            posts = posts.filter(title__icontains=title)

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
        responses={201: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER),
                'image': openapi.Schema(type=openapi.TYPE_FILE, description="Image file")
            },
            required=['title', 'description', ]
        ),
        tags=['posts'],
        security=[{'Bearer': []}]

    )
    def create_post(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if user.status_code != 200 and user.status_code != 500:
            return Response(user.json(), user.status_code)
        elif user.status_code == 500:
            return Response({"error": "internal server error"}, status.HTTP_400_BAD_REQUEST)
        serializer = PostSerializer(data=request.data, context={"user_id": user.json().get('id')})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Single post",
        operation_summary="Single post",
        responses={200: PostSerializer()},
        tags=['posts'],
    )
    def single_post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        obj = Post.objects.filter(id=pk).first()

        if not obj:
            return Response({"error": "Post not found"}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(obj)
        comments = self.get_post_comment(pk)
        if comments.status_code != 200:
            return Response({"Could not get comment"}, comments.status_code)

        return Response({"post": serializer.data, "comments": comments.json()['comments']}, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create your post",
        operation_summary="Create post",
        responses={200: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['post_id']
        ),
        tags=['posts'],
        security=[{'Bearer': []}]

    )
    def post_update(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if user.status_code != 200:
            return Response(user.json(), user.status_code)

        data = request.data
        post_id = data.get('post_id')

        post_obj = Post.objects.filter(id=post_id).first()
        if post_obj is None:
            return Response({"error": "post not found"}, status.HTTP_404_NOT_FOUND)

        if post_obj.author != user.json().get('id'):
            return Response({"error": "it is not ur post"}, status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(post_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Smth is wrong"}, status.HTTP_400_BAD_REQUEST)

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
        if user.status_code != 200 and user.status_code != 500:
            return Response(user.json(), status=user.status_code)
        elif user.status_code == 500:
            return Response({"error": "Internal server error"}, status.HTTP_400_BAD_REQUEST)
        post_id = request.data.get('post_id')
        post = Post.objects.filter(id=post_id).first()
        if not post:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

        like_obj = Like.objects.filter(post=post, author=user.json().get('id')).first()
        if like_obj:
            like_obj.delete()
            post.like_count -= 1
            post.save(update_fields=['like_count'])
            return Response({"detail": "Unliked"}, status.HTTP_200_OK)

        response = self.send_notification(user.json().get('id'))
        if response.status_code != 200 and response.status_code != 500:
            return Response(response.json(), response.status_code)
        elif response.status_code == 500:
            return Response({"error": "Server error occurred"}, status.HTTP_400_BAD_REQUEST)
        like_obj = Like.objects.create(post=post, author=user.json().get('id'))
        like_obj.save()
        post.like_count += 1
        post.save(update_fields=['like_count'])
        return Response({"detail": "Liked"}, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get all posts",
        operation_summary="get posts for users",
        responses={200: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_STRING),
                'order_by': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['token']
        ),
        tags=['microservices']
    )
    def get_posts_microservice(self, request, *args, **kwargs):
        response = self.check_services_token(request.data.get('token'))
        if response.status_code != 200:
            return Response({"error": "U are not allowed"}, status.HTTP_400_BAD_REQUEST)

        posts = Post.objects.all()
        title = request.GET.get('title', None)
        if title:
            posts = posts.filter(title__icontains=title)

        category = request.GET.get('category', None)
        if category:
            posts = posts.filter(category=category)

        order = request.GET.get('order_by', None)
        if order:
            try:
                posts = posts.order_by('order')
            except ValueError:
                pass

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Check post existence",
        operation_summary="Single post",
        responses={200: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['token', 'post_id']
        ),
        tags=['microservices']
    )
    def post_check(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token not found"}, status.HTTP_400_BAD_REQUEST)

        response = self.check_services_token(token)
        if response.status_code != 200:
            return Response({"error": "Service token is not valid"}, response.status_code)

        post_id = kwargs.get('pk')
        post_obj = Post.objects.filter(id=post_id).first()
        print(post_obj)
        if post_obj:
            if request.method == "POST":
                serializer = PostSerializer(post_obj)
                return Response(serializer.data, status.HTTP_200_OK)
            elif request.method == "DELETE":
                post_obj.delete()
                return Response({"detail": "post deleted"}, status.HTTP_200_OK)
        return Response({"error": "Post not found"}, status.HTTP_404_NOT_FOUND)

    def check_authentication(self, access_token):
        data = self.get_one_time_token()
        if data.status_code != 200:
            return data
        response = requests.post('http://134.122.76.27:8118/api/v1/auth/me/', data=data.json(),
                                 headers={"Authorization": access_token})
        return response

    def get_post_comment(self, post_id):
        data = self.get_one_time_token()
        if data.status_code != 200:
            return data
        response = requests.get('http://134.122.76.27:8117/api/v1/post/', data={"token": data.json()['token'],
                                                                                "post_id": post_id})
        return response

    def get_one_time_token(self):
        response = requests.post(url='http://134.122.76.27:8114/api/v1/login/',
                                 data={"secret_key": settings.SECRET_SERVICE_KEY,
                                       "service_id": settings.SECRET_SERVICE_ID,
                                       "service_name": settings.SECRET_SERVICE_NAME})
        return response

    def check_services_token(self, token):
        response = requests.post('http://134.122.76.27:8114/api/v1/check/',
                                 data={"token": token})
        return response

    def send_notification(self, user_id):
        token = self.get_one_time_token()
        if token.status_code != 200:
            return token
        response = requests.post('http://134.122.76.27:8112/api/v1/notification/',
                                 json={"token": token.json().get('token'),
                                       "user_id": user_id,
                                       "notification_type": 1})
        return response
