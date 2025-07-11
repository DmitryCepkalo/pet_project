# Generated by Django 5.1.1 on 2025-06-11 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0011_comment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "ordering": ["created_at"],
                "verbose_name": "комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.AddField(
            model_name="comment",
            name="is_published",
            field=models.BooleanField(
                default=True,
                help_text="Снимите галочку, чтобы скрыть публикацию.",
                verbose_name="Опубликовано",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Добавлено"),
        ),
    ]
