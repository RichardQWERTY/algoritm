# Проектирование моделей данных для SoundCloudd

## Описание проекта
SoundCloudd - веб-платформа для загрузки и прослушивания музыки, вдохновлённая SoundCloud

## Сущности (модели)

### 1. User (Пользователь)
Встроенная модель Django `django.contrib.auth.models.User`
- id (PK)
- username
- email
- password
- first_name
- last_name
- date_joined

### 2. Profile (Профиль пользователя)
- id (PK)
- user (OneToOneField → User) - связь с пользователем
- bio (TextField, blank=True) - биография артиста
- avatar (ImageField, blank=True) - аватар
- location (CharField, max_length=100, blank=True) - местоположение
- website (URLField, blank=True) - веб-сайт артиста
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 3. Genre (Жанр)
- id (PK)
- name (CharField, max_length=50, unique=True) - название жанра
- slug (SlugField, unique=True)
- description (TextField, blank=True)
- created_at (DateTimeField, auto_now_add=True)

### 4. Track (Трек)
- id (PK)
- title (CharField, max_length=200) - название трека
- slug (SlugField, unique=True)
- author (ForeignKey → User) - автор трека
- audio_file (FileField) - аудиофайл (MP3, WAV)
- cover (ImageField, blank=True) - обложка трека
- description (TextField, blank=True) - описание
- duration (DurationField, null=True) - длительность трека
- genre (ForeignKey → Genre, null=True, blank=True) - жанр
- plays_count (PositiveIntegerField, default=0) - количество прослушиваний
- downloads_allowed (BooleanField, default=False) - разрешено ли скачивание
- is_public (BooleanField, default=True) - публичный ли трек
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 5. Comment (Комментарий)
- id (PK)
- track (ForeignKey → Track) - трек
- user (ForeignKey → User) - автор комментария
- text (TextField) - текст комментария
- timestamp (PositiveIntegerField, null=True, blank=True) - момент трека в секундах
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 6. Like (Лайк)
- id (PK)
- track (ForeignKey → Track) - трек
- user (ForeignKey → User) - пользователь
- created_at (DateTimeField, auto_now_add=True)

### 7. Playlist (Плейлист)
- id (PK)
- name (CharField, max_length=200) - название плейлиста
- slug (SlugField)
- user (ForeignKey → User) - владелец плейлиста
- description (TextField, blank=True)
- cover (ImageField, blank=True) - обложка плейлиста
- is_public (BooleanField, default=True) - публичный ли плейлист
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

### 8. PlaylistTrack (Связь плейлиста и трека)
- id (PK)
- playlist (ForeignKey → Playlist) - плейлист
- track (ForeignKey → Track) - трек
- order (PositiveIntegerField, default=0) - порядок трека в плейлисте
- added_at (DateTimeField, auto_now_add=True)

### 9. Follow (Подписка)
- id (PK)
- follower (ForeignKey → User) - подписчик
- following (ForeignKey → User) - на кого подписан
- created_at (DateTimeField, auto_now_add=True)

### 10. Play (История прослушиваний)
- id (PK)
- track (ForeignKey → Track) - трек
- user (ForeignKey → User, null=True, blank=True) - пользователь (может быть анонимным)
- ip_address (GenericIPAddressField, null=True) - IP для анонимных
- played_at (DateTimeField, auto_now_add=True)

## Связи между моделями

### One-to-One (1:1):
1. **User → Profile** (у каждого пользователя один профиль)

### One-to-Many (ForeignKey):
1. **User → Track** (пользователь может загрузить много треков)
2. **Genre → Track** (жанр содержит много треков)
3. **Track → Comment** (у трека может быть много комментариев)
4. **User → Comment** (пользователь может оставить много комментариев)
5. **Track → Like** (у трека может быть много лайков)
6. **User → Like** (пользователь может лайкнуть много треков)
7. **User → Playlist** (пользователь может создать много плейлистов)
8. **Playlist → PlaylistTrack** (плейлист содержит много треков)
9. **Track → PlaylistTrack** (трек может быть в разных плейлистах)
10. **User → Follow** (пользователь может подписаться на многих)
11. **Track → Play** (у трека много прослушиваний)
12. **User → Play** (пользователь прослушал много треков)

## ER-диаграмма (текстовое представление)

```
┌─────────────┐
│    User     │
│  (Django)   │
└──────┬──────┘
       │
       │ 1:1
       ▼
┌─────────────┐
│   Profile   │
│             │
│    user     │
└─────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │
       │ 1:N
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│    Track    │    │  Playlist   │
│             │    │             │
│   author    │    │    user     │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │ N:1              │ 1:N
       ▼                  ▼
┌─────────────┐    ┌──────────────┐
│    Genre    │    │PlaylistTrack │
│             │    │              │
└─────────────┘    │  playlist    │
                   │   track      │
                   └──────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────┐
│   Comment   │
│             │
│    user     │
│   track     │
└──────┬──────┘
       │ N:1
       ▼
┌─────────────┐
│    Track    │
└─────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────┐
│    Like     │
│             │
│    user     │
│   track     │
└──────┬──────┘
       │ N:1
       ▼
┌─────────────┐
│    Track    │
└─────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├─────────┐
       │         │
       ▼         ▼
    follower  following
       │         │
       └────┬────┘
            ▼
      ┌─────────────┐
      │   Follow    │
      └─────────────┘
```

## Индексы и ограничения

### Уникальные ограничения:
- Profile.user - уникальный (OneToOne)
- Genre.name - уникальный
- Genre.slug - уникальный
- Track.slug - уникальный
- Like: уникальная пара (user, track) - один пользователь может лайкнуть трек только один раз
- Follow: уникальная пара (follower, following) - нельзя подписаться дважды

### Составные уникальные ограничения:
- PlaylistTrack: уникальная пара (playlist, track) - трек не может быть дважды в одном плейлисте

### Индексы для оптимизации:
- Track.author (ForeignKey автоматически создаёт индекс)
- Track.genre (ForeignKey автоматически создаёт индекс)
- Track.created_at (для сортировки новых треков)
- Track.plays_count (для популярных треков)
- Comment.track + Comment.created_at (для получения комментариев)
- Like.track (для подсчёта лайков)
- Playlist.user (для получения плейлистов пользователя)
- Follow.follower (для получения подписок)
- Follow.following (для получения подписчиков)
- Play.track + Play.played_at (для статистики)

## Валидация данных

### Track:
- audio_file: только MP3, WAV форматы
- duration > 0
- title не пустое

### Comment:
- text не пустое
- timestamp >= 0 и <= длительности трека

### PlaylistTrack:
- order >= 0

### Follow:
- follower != following (нельзя подписаться на себя)

## Методы моделей

### Profile:
- `get_absolute_url()` - URL профиля
- `get_followers_count()` - количество подписчиков
- `get_following_count()` - количество подписок

### Track:
- `get_absolute_url()` - URL трека
- `get_likes_count()` - количество лайков
- `get_comments_count()` - количество комментариев
- `increment_plays()` - увеличить счётчик прослушиваний
- `is_liked_by(user)` - лайкнул ли пользователь трек

### Playlist:
- `get_absolute_url()` - URL плейлиста
- `get_tracks_count()` - количество треков
- `get_duration()` - общая длительность плейлиста

### User (через Profile):
- `get_tracks_count()` - количество треков пользователя
- `get_total_plays()` - общее количество прослушиваний всех треков

## Примечания для реализации

1. Использовать `django.contrib.auth` для User
2. Для аудиофайлов установить `mutagen` для чтения метаданных
3. Для изображений установить `Pillow`
4. Настроить `MEDIA_ROOT` и `MEDIA_URL` для загрузки файлов
5. Использовать `django-cleanup` для автоматического удаления файлов
6. Добавить `__str__()` методы для всех моделей
7. Использовать `select_related()` и `prefetch_related()` для оптимизации запросов
8. Для аудиоплеера использовать Howler.js или HTML5 Audio API
9. Для визуализации волны использовать WaveSurfer.js (опционально)
10. Добавить сигналы для автоматического создания Profile при регистрации User
