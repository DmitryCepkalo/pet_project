from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    Заголовок = serializers.CharField(source='title')
    Текст = serializers.CharField(source='text')
    Дата_публикации = serializers.DateTimeField(source='pub_date')

    class Meta:
        model = Post
        fields = ['id', 'Заголовок', 'Текст', 'Дата_публикации']