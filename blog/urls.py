from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .api_views import PostViewSet
from .views import (
    IndexView,
    PostDetailView,
    CategoryPostListView,
    UserProfileView,
    CreatePostView,
    PostEditView,
    EditCommentView,
    DeleteCommentView,
    DeletePostView,
    AddCommentView,
    EditProfileView,
    UserPostListView
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
app_name = 'blog'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    # Посты
    path('posts/create/',
         CreatePostView.as_view(), name='create_post'),
    path('posts/<int:post_id>/',
         PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/',
         PostEditView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         DeletePostView.as_view(), name='delete_post'),

    # Комментарии к постам
    path('posts/<int:post_id>/comment/',
         AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         DeleteCommentView.as_view(), name='delete_comment'),

    # Категории
    path('category/<slug:category_slug>/',
         CategoryPostListView.as_view(), name='category_posts'),

    # Профиль пользователя
    path('profile/edit/',
         EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/',
         UserProfileView.as_view(), name='profile'),
    path('user/<str:username>/',
         UserPostListView.as_view(), name='user_posts'),
    # REST API
    path('api/', include(router.urls)),
]
