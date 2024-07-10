from django.urls import path
from rest_framework import views
from .views import PostViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('posts/', PostViewSet.as_view({"get": "get_posts"})),
    path('post/delete/', PostViewSet.as_view({"delete": "post_delete"})),
    path('post/create/', PostViewSet.as_view({"post": "create_post"})),
    path('post/<int:pk>/', PostViewSet.as_view({"get": "retrieve"})),
    path('like-unlike/', PostViewSet.as_view({"post": "like_unlike_post"})),
]
