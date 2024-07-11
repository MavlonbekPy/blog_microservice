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
        # Remove the image field from validated_data if it's not present in the request data
        if 'image' in validated_data:
            validated_data.pop('image')
        if 'author' in validated_data:
            validated_data.pop('author')

        return super().update(instance, validated_data)





