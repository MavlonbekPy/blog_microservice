from django.urls import path
from rest_framework import views
from .views import PostViewSet, LikePostViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

posts_list = PostViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
posts_detail = PostViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    path('posts/', PostViewSet.as_view({"get": "get_posts"})),
    path('posts/<int:pk>/', posts_detail, name='post-detail'),
    path('post/delete/', PostViewSet.as_view({"delete": "post_delete"})),
    path('post/create/', PostViewSet.as_view({"put": "create_post"})),
    # path('post_By_user')
    # path('like_to_post')
    path('like-unlike/', LikePostViewSet.as_view({"post": "like_unlike_post"})),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger')
]
