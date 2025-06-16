from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from .constants import Lengths

User = get_user_model()


class AbstractPublishModel(models.Model):
    """
    Абстрактная модель для объектов с публикацией.
    Добавляет флаг публикации и дату создания.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class TruncatedStringMixin:
    """Миксин для обрезания строкового атрибута в __str__."""

    STR_ATTR_NAME = 'title'
    MAX_LENGTH = 50
    ELLIPSIS = '...'

    class Meta:
        abstract = True

    def __str__(self):
        value = getattr(self, self.STR_ATTR_NAME, '')
        str_value = str(value)

        if value:
            if len(str_value) > self.MAX_LENGTH:
                return str_value[:self.MAX_LENGTH] + self.ELLIPSIS
            return str_value
        return super().__str__()


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related('author', 'category', 'location')
            .filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )
        )


class Category(TruncatedStringMixin, AbstractPublishModel):
    STR_ATTR_NAME = 'title'
    title = models.CharField(
        max_length=Lengths.TITLE,
        verbose_name='Заголовок',
        help_text=f'Максимальная длина – {Lengths.TITLE} символов',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    slug = models.SlugField(
        max_length=Lengths.SLUG,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Location(TruncatedStringMixin, AbstractPublishModel):
    STR_ATTR_NAME = 'name'
    name = models.CharField(
        max_length=Lengths.TITLE,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ['name']


class Post(TruncatedStringMixin, AbstractPublishModel):
    title = models.CharField(
        max_length=Lengths.TITLE,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — можно делать '
                   'отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        upload_to='posts_images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        default_related_name = 'posts'


class Comment(TruncatedStringMixin, AbstractPublishModel):
    STR_ATTR_NAME = 'text'

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
