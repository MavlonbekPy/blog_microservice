from django.contrib import admin
from blog.models import Post, Category


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
