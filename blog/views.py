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

    )  # notification
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
        tags=['get-posts']
    )
    def get_posts(self, request, *args, **kwargs):
        size = request.GET.get('size')
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

        # Return the paginated response
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

    )  # notification
    def create_post(self, request, *args, **kwargs):
        user = self.check_authentication(request.headers.get('Authorization'))
        if user.status_code != 200:
            return Response(user.json(), user.status_code)
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
    )  # comment # tag
    def single_post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        obj = Post.objects.filter(id=pk).first()

        if not obj:
            return Response({"error": "Post not found"}, status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(obj)
        # comments = self.get_post_comment(pk)
        # if comments.status_code != 200:
        #     return Response(comments.json(), comments.status_code)

        return Response({"post": serializer.data}, status.HTTP_200_OK)

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

    @swagger_auto_schema(
        operation_description="Get all posts",
        operation_summary="get posts for users",
        manual_parameters=[
            openapi.Parameter('page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter('title', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter('category', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY),
            openapi.Parameter('order_by', type=openapi.TYPE_STRING, in_=openapi.IN_QUERY)
        ],
        responses={200: PostSerializer()},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['token']
        ),
        tags=['get-post-list-for-services']
    )
    def get_posts(self, request, *args, **kwargs):
        response = self.check_services_token(request.data.get('token'))
        if response.status_code != 200:
            return Response({"error": "U are not allowed"}, status.HTTP_400_BAD_REQUEST)
        size = request.GET.get('size')
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

        order = request.GET.get('order_by', None)
        if order:
            try:
                posts = posts.order_by('order')
            except ValueError:
                pass

        paginator = PageNumberPagination()
        paginator.page_size = size

        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)

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
        data.json()['post_id'] = post_id
        response = requests.get('', data=data.json())
        return response

    def get_one_time_token(self):
        response = requests.post(url='http://134.122.76.27:8114/api/v1/login/',
                                 data={"secret_key": settings.SECRET_SERVICE_KEY,
                                       "service_id": settings.SECRET_SERVICE_ID,
                                       "service_name": settings.SECRET_SERVICE_NAME})
        return response

    def check_services_token(self, token):
        response = requests.post('http://134.122.76.27:8114/api/v1/check/', data={"token": token})
        return response


@api_view(["GET"])
def create_post_view(request):
    for i in range(1000):
        post = Post(title=f"Post {i}", description=f"Post {i}", author=random.randint(1, 20), category_id=1)
        post.save()
    return Response({"message": "Post"})
