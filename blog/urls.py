from django.urls import path
from .views import PostViewSet

urlpatterns = [
    path('posts/', PostViewSet.as_view({"get": "get_posts"})),
    path('posts/list/', PostViewSet.as_view({"post": "get_posts_microservice"})),
    path('post/<int:pk>/', PostViewSet.as_view({"delete": "post_delete",
                                                "patch": "post_update",
                                                "get": "single_post", })),
    path('post/create/', PostViewSet.as_view({"post": "create_post"})),
    path('like-unlike/', PostViewSet.as_view({"post": "like_unlike_post"})),
    path('post/detail-delete/<int:pk>/', PostViewSet.as_view({"post": "post_check",
                                                              "delete": "post_check"})),
    path('post/update-comment/', PostViewSet.as_view({"post": "comment_update"})),
]
