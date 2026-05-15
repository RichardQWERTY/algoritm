from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify #для понятных названий
class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название жанра"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL идентификатор",
        help_text="строка для URL"
    )
    description = models.TextField(
        verbose_name="Описание жанра"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

class Profile(models.Model): #профиль ака аккаунт
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    bio = models.TextField(
        verbose_name="О себе",
        blank=True
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватарка",
        blank=True,
        null=True
    )
    location = models.CharField(
        max_length=100,
        verbose_name="Местоположение",
        blank=True
    )
    website = models.URLField(
        max_length=200,
        verbose_name="Сайт",
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class Track(models.Model): #целый трек
        title = models.CharField(
            max_length=200,
            verbose_name="Название трека"
        )
        slug = models.SlugField(
            max_length=200,
            unique=True,
            verbose_name="URL идентификатор"
        )
        author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='tracks',
            verbose_name="Автор"
        )
        audio_file = models.FileField(
            upload_to='tracks/',
            verbose_name="Аудиофайл"
        )
        cover = models.ImageField(
            upload_to='covers/',
            verbose_name="Обложка",
            blank=True,
            null=True
        )
        description = models.TextField(
            verbose_name="Описание",
            blank=True
        )
        genre = models.ForeignKey(
            Genre,
            on_delete=models.PROTECT,
            verbose_name="Жанр"
        )
        plays_count = models.PositiveIntegerField(
            default=0,
            verbose_name="Количество прослушиваний"
        )
        downloads_allowed = models.BooleanField(
            default=True,
            verbose_name="Разрешено скачивание"
        )
        is_public = models.BooleanField(
            default=True,
            verbose_name="Публичный трек"
        )
        created_at = models.DateTimeField(
            auto_now_add=True,
            verbose_name="Дата загрузки"
        )
        updated_at = models.DateTimeField(
            auto_now=True,
            verbose_name="Дата обновления"
        )

        def save(self, *args, **kwargs): #автоматическое создание slug из названия, если это поле пустое
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)

        def __str__(self):
            return self.title

        class Meta:
            verbose_name = "Трек"
            verbose_name_plural = "Треки"
            ordering = ['-created_at']

class Comment(models.Model): #комментарии к таймкоду трека
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Трек"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария"
    )
    text = models.TextField(verbose_name="Текст комментария")
    timestamp = models.PositiveIntegerField(
        verbose_name="Время",
        help_text="Время в секундах от начала трека"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return f"{self.user} → {self.track}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

class Like(models.Model): #лайки треков
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Трек"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата лайка"
    )

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        unique_together = ('track', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} liked {self.track}"

class Playlist(models.Model): #плейлисты пользователя
    name = models.CharField(
        max_length=200,
        verbose_name="Название плейлиста"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL идентификатор"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name="Владелец"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True
    )
    cover = models.ImageField(
        upload_to='playlists/',
        verbose_name="Обложка плейлиста",
        blank=True,
        null=True
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name="Публичный плейлист"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Плейлист"
        verbose_name_plural = "Плейлисты"
        ordering = ['-created_at']

class PlaylistTrack(models.Model): #расположение треков в плейлисте
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name="Плейлист"
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        verbose_name="Трек"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Трек в плейлисте"
        verbose_name_plural = "Треки в плейлисте"
        unique_together = ('playlist', 'track')
        ordering = ['order']

    def __str__(self):
        return f"{self.track} в {self.playlist}"

class Follow(models.Model): #подписки пользователей
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Подписчик"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="На кого подписан"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} подписан на {self.following}"

class Play(models.Model): #история прослушивания
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        verbose_name="Трек"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="IP адрес"
    )
    played_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время прослушивания"
    )

    def __str__(self):
        return f"Play {self.track} by {self.user or self.ip_address}"

    class Meta:
        verbose_name = "Прослушивание"
        verbose_name_plural = "Прослушивания"
        ordering = ['-played_at']

