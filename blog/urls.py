from django.urls import path
from .views import PostViewSet, create_post_view

urlpatterns = [
    path('posts/', PostViewSet.as_view({"get": "get_posts"})),
    path('post/delete/', PostViewSet.as_view({"delete": "post_delete"})),
    path('post/create/', PostViewSet.as_view({"post": "create_post"})),
    path('post/<int:pk>/', PostViewSet.as_view({"get": "single_post"})),
    path('like-unlike/', PostViewSet.as_view({"post": "like_unlike_post"})),
    path('post/update/', PostViewSet.as_view({"patch": "post_update"})),
    path('post/', create_post_view,)
]
