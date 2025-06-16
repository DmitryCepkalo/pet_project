from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Location, Post, Comment

admin.site.site_header = 'Панель администратора'
admin.site.site_title = 'Блог'
admin.site.index_title = 'Управление контентом'
admin.site.unregister(Group)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'description')
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке
    list_display = (
        'title',
        'author',
        'pub_date',
        'category',
        'location',
        'is_published'
    )

    # Поля, которые можно редактировать прямо в списке
    list_editable = ('is_published',)

    # Фильтры в правой панели
    list_filter = (
        'is_published',
        'category',
        'pub_date',
        'author'
    )

    # Поля для поиска
    search_fields = ('title', 'text', 'author__username')

    # Группировка полей в форме редактирования
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'author', 'image')
        }),
        ('Публикация', {
            'fields': ('pub_date', 'is_published', 'category', 'location'),
        }),
    )

    # Оптимизация запросов к БД
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author',
                                                            'category',
                                                            'location')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('is_published', 'created_at', 'author', 'post')
    raw_id_fields = ('author', 'post')
