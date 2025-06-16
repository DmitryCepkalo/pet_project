
class Lengths:
    """Константы для ограничения длины полей."""

    TITLE = 256
    """
    Максимальная длина заголовков (Category.title, Post.title, Location.name).
    """

    SLUG = 64
    """Максимальная длина slug-идентификаторов."""


class PostLimits:
    LATEST_POSTS_COUNT = 10
    """Количество последних постов на главной."""
