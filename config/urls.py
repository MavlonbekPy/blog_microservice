from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",

        default_version='v1', ),
    public=True,
    permission_classes=[AllowAny, ],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('blog.urls')),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]
