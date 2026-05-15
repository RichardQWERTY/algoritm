"""
Модели данных для SoundCloudd - музыкальной платформы
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Профиль пользователя (артиста)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d',
        blank=True,
        verbose_name='Аватар'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Местоположение'
    )
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_absolute_url(self):
        return reverse('users:profile', args=[self.user.username])

    def get_followers_count(self):
        """Количество подписчиков"""
        return Follow.objects.filter(following=self.user).count()

    def get_following_count(self):
        """Количество подписок"""
        return Follow.objects.filter(follower=self.user).count()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматическое создание профиля при регистрации"""
    if created:
        Profile.objects.create(user=instance)


class Genre(models.Model):
    """Музыкальный жанр"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tracks:genre', args=[self.slug])


class Track(models.Model):
    """Музыкальный трек"""
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Автор'
    )
    audio_file = models.FileField(
        upload_to='tracks/%Y/%m/%d',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav'])],
        verbose_name='Аудиофайл'
    )
    cover = models.ImageField(
        upload_to='covers/%Y/%m/%d',
        blank=True,
        verbose_name='Обложка'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    duration = models.DurationField(null=True, blank=True, verbose_name='Длительность')
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracks',
        verbose_name='Жанр'
    )
    plays_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Прослушивания'
    )
    downloads_allowed = models.BooleanField(
        default=False,
        verbose_name='Разрешено скачивание'
    )
    is_public = models.BooleanField(default=True, verbose_name='Публичный')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-plays_count']),
        ]

    def __str__(self):
        return f'{self.author.username} - {self.title}'

    def get_absolute_url(self):
        return reverse('tracks:detail', args=[self.slug])

    def get_likes_count(self):
        """Количество лайков"""
        return self.likes.count()

    def get_comments_count(self):
        """Количество комментариев"""
        return self.comments.count()

    def increment_plays(self):
        """Увеличить счётчик прослушиваний"""
        self.plays_count += 1
        self.save(update_fields=['plays_count'])

    def is_liked_by(self, user):
        """Проверка, лайкнул ли пользователь трек"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Comment(models.Model):
    """Комментарий к треку"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Трек'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    timestamp = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Момент трека (сек)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['track', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.text[:50]}'


class Like(models.Model):
    """Лайк трека"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Трек'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ['user', 'track']
        indexes = [
            models.Index(fields=['track']),
        ]

    def __str__(self):
        return f'{self.user.username} лайкнул {self.track.title}'


class Playlist(models.Model):
    """Плейлист"""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, verbose_name='URL')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name='Владелец'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    cover = models.ImageField(
        upload_to='playlists/%Y/%m/%d',
        blank=True,
        verbose_name='Обложка'
    )
    is_public = models.BooleanField(default=True, verbose_name='Публичный')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.name}'

    def get_absolute_url(self):
        return reverse('tracks:playlist', args=[self.user.username, self.slug])

    def get_tracks_count(self):
        """Количество треков в плейлисте"""
        return self.playlist_tracks.count()

    def get_duration(self):
        """Общая длительность плейлиста"""
        from datetime import timedelta
        total = timedelta()
        for pt in self.playlist_tracks.select_related('track'):
            if pt.track.duration:
                total += pt.track.duration
        return total


class PlaylistTrack(models.Model):
    """Связь плейлиста и трека"""
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_tracks',
        verbose_name='Плейлист'
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='playlist_tracks',
        verbose_name='Трек'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')

    class Meta:
        verbose_name = 'Трек в плейлисте'
        verbose_name_plural = 'Треки в плейлистах'
        ordering = ['order', 'added_at']
        unique_together = ['playlist', 'track']

    def __str__(self):
        return f'{self.playlist.name} - {self.track.title}'


class Follow(models.Model):
    """Подписка на пользователя"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='На кого подписан'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f'{self.follower.username} подписан на {self.following.username}'

    def clean(self):
        """Валидация: нельзя подписаться на себя"""
        from django.core.exceptions import ValidationError
        if self.follower == self.following:
            raise ValidationError('Нельзя подписаться на себя')


class Play(models.Model):
    """История прослушиваний"""
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='plays',
        verbose_name='Трек'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plays',
        verbose_name='Пользователь'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )
    played_at = models.DateTimeField(auto_now_add=True, verbose_name='Прослушан')

    class Meta:
        verbose_name = 'Прослушивание'
        verbose_name_plural = 'Прослушивания'
        ordering = ['-played_at']
        indexes = [
            models.Index(fields=['track', '-played_at']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else self.ip_address
        return f'{user_str} прослушал {self.track.title}'
