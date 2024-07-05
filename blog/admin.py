from django.contrib import admin
from .models import Post, Category, Tag


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
