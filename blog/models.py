from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)

    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Like(models.Model):
    author = models.IntegerField()
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
