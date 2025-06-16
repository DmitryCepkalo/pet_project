from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class UserEditForm(forms.ModelForm):
    """Форма редактирования данных пользователя."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'image',
            'is_published'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pub_date:
            self.initial[
                'pub_date'] = self.instance.pub_date.strftime('%Y-%m-%dT%H:%M')


class CommentForm(forms.ModelForm):
    """Форма для создания и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ['text']
