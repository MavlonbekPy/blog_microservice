import requests
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import Post, Like
from .serializers import PostSerializer


class PostViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

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
        user = self.check_authentication(request.user)
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

    def check_authentication(self, user):
        response = requests.get('', data=user)
        if response.status_code == 200:
            return response.json()
        return False
