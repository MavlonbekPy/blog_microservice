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





