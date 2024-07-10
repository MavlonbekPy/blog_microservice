from django.contrib import admin
from .models import Post, Category, Like


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Like)
