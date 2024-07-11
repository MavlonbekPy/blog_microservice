from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def save(self, **kwargs):
        user_id = self.context.get('user_id')
        if user_id:
            self.validated_data['author'] = user_id
        return super().save(**kwargs)

    def update(self, instance, validated_data):
        validated_data.pop('image', None)
        validated_data.pop('author', None)
        validated_data.pop('like_count', None)
        validated_data.pop('comment_count', None)
        validated_data.pop('view_count', None)
        validated_data.pop('created_at', None)
        validated_data.pop('updated_at', None)
        return super().update(instance, validated_data)





