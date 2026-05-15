from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Связь один к одному с пользователем (Заменяет UNIQUE FOREIGN KEY)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField()
    avatar = models.CharField(max_length=255) # Для реальных файлов лучше использовать ImageField/FileField
    location = models.CharField(max_length=100)
    website = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль: {self.user.username}"


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Track(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    audio_file = models.CharField(max_length=255) # На практике: models.FileField(upload_to='tracks/')
    cover = models.CharField(max_length=255)      # На практике: models.ImageField(upload_to='covers/')
    description = models.TextField()
    # ON DELETE RESTRICT преобразуется в models.RESTRICT
    genre = models.ForeignKey(Genre, on_delete=models.RESTRICT, related_name='tracks')
    plays_count = models.IntegerField(default=0)
    downloads_allowed = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.IntegerField()  # Секунды от начала трека
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.track.title}"


class Like(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Уникальный индекс на пару трек-пользователь
        constraints = [
            models.UniqueConstraint(fields=['track', 'user'], name='unique_like')
        ]

    def __str__(self):
        return f"{self.user.username} оценил {self.track.title}"


class Playlist(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    description = models.TextField()
    cover = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)
    # Связь ManyToMany через промежуточную таблицу playlist_tracks
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    order = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Уникальный индекс на пару плейлист-трек
        constraints = [
            models.UniqueConstraint(fields=['playlist', 'track'], name='unique_playlist_track')
        ]
        ordering = ['order']


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow')
        ]

    def __str__(self):
        return f"{self.follower.username} подписан на {self.following.username}"


class Play(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='plays')
    # ON DELETE SET NULL требует, чтобы поле могло принимать null значения в Django (null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='plays')
    ip_address = models.GenericIPAddressField()  # Заменяет тип INET из SQL
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Прослушивание {self.track.title} в {self.played_at}"