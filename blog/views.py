from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View, DeleteView
)
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Category, Post, Comment
from .forms import UserEditForm, PostForm, CommentForm
from .constants import PostLimits

User = get_user_model()


def paginate(request, queryset, per_page=PostLimits.LATEST_POSTS_COUNT):
    """Универсальная функция пагинации."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


class CommentContextMixin:
    """Миксин для добавления комментария в контекст шаблона."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        return context


class IndexView(ListView):
    """
    Главная страница с последними опубликованными постами,
    отсортированными по дате публикации (от новых к старым).
    """

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = PostLimits.LATEST_POSTS_COUNT

    def get_queryset(self):
        """
        Получить опубликованные посты
        с аннотацией количества комментариев,
        отсортированные по убыванию даты публикации.
        """
        return Post.published.annotate(
            comment_count=Count('comments')).order_by('-pub_date')


# =================================
# Все, связанное с пользователем.
# =================================
class UserProfileView(View):
    """
    Профиль пользователя с его постами.
    Если текущий пользователь — владелец профиля, показываем все посты,
    иначе — только опубликованные.
    """

    def get(self, request, username):
        profile_user = get_object_or_404(User, username=username)

        if request.user == profile_user:
            queryset = Post.objects
        else:
            queryset = Post.published

        post_list = (
            queryset
            .filter(author=profile_user)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

        page_obj = paginate(request, post_list)

        full_name = profile_user.get_full_name()
        profile_user.get_full_name = (
            lambda: full_name if full_name.strip() else ''
        )

        return render(request, 'blog/profile.html', {
            'profile': profile_user,
            'page_obj': page_obj,
            'is_owner': request.user == profile_user,
            'now': timezone.now(),
        })


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля пользователя.
    Пользователь может редактировать только свои данные.
    """

    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Возвращает текущего аутентифицированного пользователя."""
        return self.request.user

    def get_success_url(self):
        """URL для редиректа после успешного сохранения профиля."""
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    """
    Страница с подробной информацией о посте и его комментариями.
    Показывает все посты автора, если пользователь — автор,
    иначе — только опубликованные.
    """

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self):
        """
        Возвращает QuerySet
        в зависимости от аутентификации пользователя.
        """
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            return qs.filter(Q(is_published=True) | Q(author=user))
        return qs.filter(is_published=True)

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст форму
        для комментариев и список комментариев поста.
        """
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all()
        context['form'] = CommentForm()
        return context


# =================================
# Списки постов.
# =================================
class CategoryPostListView(View):
    """
    Список опубликованных постов
    выбранной категории.
    """

    def get(self, request, category_slug):
        category = get_object_or_404(
            Category, slug=category_slug, is_published=True)
        post_list = Post.published.filter(category=category)
        page_obj = paginate(request, post_list)
        return render(request, 'blog/category.html', {
            'category': category,
            'page_obj': page_obj
        })


class UserPostListView(View):
    """
    Список опубликованных постов
    пользователя с подсчётом комментариев.
    """

    def get(self, request, username):
        post_list = (
            Post.published
            .filter(author__username=username)
            .annotate(comment_count=Count('comments'))
        )
        page_obj = paginate(request, post_list)
        return render(request, 'blog/user.html', {'page_obj': page_obj})


# =================================
# Вьюхи для постов пользователя.
# =================================
class CreatePostView(LoginRequiredMixin, CreateView):
    """
    Создание нового поста. Автором становится текущий пользователь.
    Если дата публикации в будущем — пост автоматически не публикуется.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        if post.pub_date > timezone.now():
            post.is_published = False
        post.save()
        return redirect('blog:profile', username=self.request.user.username)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование поста.
    Только автор может редактировать свой пост.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        """Проверяет, является ли текущий пользователь автором поста."""
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        """Редирект на страницу поста, если доступ запрещён."""
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        """URL для редиректа после успешного редактирования поста."""
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class DeletePostView(LoginRequiredMixin, DeleteView):
    """
    Удаление поста.
    Только автор поста может удалить.
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        """URL для редиректа после успешного удаления поста."""
        return reverse('blog:index')

    def get_queryset(self):
        """Ограничиваем выборку постов только постами текущего пользователя."""
        return self.request.user.posts.all()


# =================================
# Вьюхи для комментариев.
# =================================
class AddCommentView(LoginRequiredMixin, View):
    """Добавление комментария к посту."""

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
        return redirect('blog:post_detail', post_id=post.id)


class EditCommentView(LoginRequiredMixin,
                      UserPassesTestMixin,
                      CommentContextMixin,
                      UpdateView):
    """
    Редактирование комментария.
    Только автор комментария имеет доступ.
    """

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        """Проверяет, является ли текущий пользователь автором комментария."""
        comment = self.get_object()
        return comment.author == self.request.user

    def form_valid(self, form):
        """Сохраняет изменённый комментарий."""
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = self.get_object().post
        comment.save()
        return redirect('blog:post_detail', post_id=comment.post.id)


class DeleteCommentView(LoginRequiredMixin,
                        UserPassesTestMixin,
                        CommentContextMixin,
                        DeleteView):
    """
    Удаление комментария.
    Только автор комментария имеет доступ.
    """

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        """Проверяет, является ли текущий пользователь автором комментария."""
        comment = self.get_object()
        return comment.author == self.request.user

    def form_valid(self, form):
        """Удаляет комментарий и перенаправляет на страницу поста."""
        post_id = self.object.post.id
        self.object.delete()
        return redirect('blog:post_detail', post_id=post_id)
