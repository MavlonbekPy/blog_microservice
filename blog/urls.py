from django.urls import path
from rest_framework import views
from .views import PostViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

posts_list = PostViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
posts_detail = PostViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path('posts/', posts_list, name='post-list-create'),
    path('posts/<int:pk>/', posts_detail, name='post-detail'),
    # path('post_By_user')
    # path('like_to_post')
    # path('')
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger')
]
