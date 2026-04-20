# Инструкция по использованию ER-диаграммы SoundCloudd

## Файлы в этой папке

1. **ER-диаграмма.md** - подробное текстовое описание всех моделей данных
2. **models.py** - готовый код моделей Django для копирования в проект
3. **database_schema.dbml** - схема базы данных для визуализации
4. **визуальная_диаграмма.txt** - ASCII-диаграмма для быстрого просмотра
5. **README.md** - этот файл с инструкциями

## О проекте

**SoundCloudd** - веб-платформа для загрузки и прослушивания музыки, вдохновлённая SoundCloud.

### Основные возможности:
- 🎧 Загрузка и прослушивание аудиофайлов (MP3, WAV)
- 💬 Комментарии к трекам (в том числе к конкретному моменту)
- ❤️ Лайки треков
- 📚 Создание плейлистов
- 👥 Подписки на артистов
- 📊 Статистика прослушиваний
- 🏷️ Категоризация по жанрам

## Как визуализировать диаграмму

### Вариант 1: dbdiagram.io (рекомендуется)
1. Откройте https://dbdiagram.io/
2. Скопируйте содержимое файла `database_schema.dbml`
3. Вставьте в редактор на сайте
4. Диаграмма построится автоматически
5. Можно экспортировать в PNG, PDF или SQL

### Вариант 2: draw.io
1. Откройте https://app.diagrams.net/
2. Создайте новую диаграмму
3. Используйте описание из `ER-диаграмма.md` для создания схемы вручную
4. Используйте фигуры "Entity Relation" из библиотеки

### Вариант 3: Ручная схема
Можно нарисовать схему от руки на бумаге, используя описание из `ER-диаграмма.md`

## Описание моделей

### Основные сущности:

1. **User** - пользователи системы (встроенная модель Django)
2. **Profile** - профиль пользователя/артиста (1:1 с User)
3. **Genre** - музыкальные жанры
4. **Track** - музыкальные треки
5. **Comment** - комментарии к трекам
6. **Like** - лайки треков
7. **Playlist** - плейлисты пользователей
8. **PlaylistTrack** - связь плейлиста и трека (с порядком)
9. **Follow** - подписки на пользователей
10. **Play** - история прослушиваний

### Типы связей:

#### One-to-One (1:1):
- **User → Profile** (у каждого пользователя один профиль)

#### One-to-Many (ForeignKey):
- **User → Track** (пользователь может загрузить много треков)
- **Genre → Track** (жанр содержит много треков)
- **Track → Comment** (у трека много комментариев)
- **User → Comment** (пользователь может оставить много комментариев)
- **Track → Like** (у трека много лайков)
- **User → Like** (пользователь может лайкнуть много треков)
- **User → Playlist** (пользователь может создать много плейлистов)
- **Playlist → PlaylistTrack** (плейлист содержит много треков)
- **Track → PlaylistTrack** (трек может быть в разных плейлистах)
- **User → Follow** (подписки - самосвязь)
- **Track → Play** (у трека много прослушиваний)
- **User → Play** (пользователь прослушал много треков)

## Следующие шаги

После утверждения ER-диаграммы:

### 1. Создать Django проект
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install django pillow mutagen django-cleanup
django-admin startproject soundcloudd
cd soundcloudd
python manage.py startapp tracks
python manage.py startapp users
```

### 2. Скопировать модели
- Скопируйте код из `models.py` в файлы `tracks/models.py` и `users/models.py`
- Распределите модели по приложениям:
  - **users/models.py**: Profile, Follow
  - **tracks/models.py**: Genre, Track, Comment, Like, Playlist, PlaylistTrack, Play

### 3. Настроить settings.py
```python
INSTALLED_APPS = [
    ...
    'tracks',
    'users',
    'django_cleanup.apps.CleanupConfig',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4. Создать и применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Зарегистрировать модели в admin.py
```python
# tracks/admin.py
from django.contrib import admin
from .models import Genre, Track, Comment, Like, Playlist, PlaylistTrack, Play

admin.site.register(Genre)
admin.site.register(Track)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Playlist)
admin.site.register(PlaylistTrack)
admin.site.register(Play)

# users/admin.py
from django.contrib import admin
from .models import Profile, Follow

admin.site.register(Profile)
admin.site.register(Follow)
```

### 6. Создать суперпользователя
```bash
python manage.py createsuperuser
```

## Особенности реализации

### Валидация:
- Аудиофайлы: только MP3, WAV форматы
- Комментарий: timestamp >= 0
- Follow: нельзя подписаться на себя
- Like: один пользователь = один лайк на трек
- PlaylistTrack: трек один раз в плейлисте

### Индексы для оптимизации:
- Track: (author, genre, created_at, plays_count)
- Comment: (track, created_at)
- Like: track
- Playlist: user
- Follow: (follower, following)
- Play: (track, played_at)

### Автоматические действия:
- Profile создаётся автоматически при регистрации User (через сигнал)
- Файлы удаляются автоматически при удалении объекта (django-cleanup)

### Методы моделей:
- **Profile**: get_followers_count(), get_following_count()
- **Track**: get_likes_count(), get_comments_count(), increment_plays(), is_liked_by(user)
- **Playlist**: get_tracks_count(), get_duration()

## Уникальные фичи проекта

### MVP (обязательно):
1. ✅ Регистрация и авторизация
2. ✅ Загрузка аудиофайлов с обложкой
3. ✅ Страница трека с плеером
4. ✅ Лента треков
5. ✅ Профиль пользователя
6. ✅ Лайки и комментарии
7. ✅ Поиск по трекам

### Дополнительные фичи (опционально):
1. 🌊 **Визуализация волны** - WaveSurfer.js
2. ⏱️ **Комментарии к моменту трека** - поле timestamp в Comment
3. 📚 **Плейлисты** - модели Playlist, PlaylistTrack
4. 🏷️ **Жанры** - модель Genre
5. 📊 **Статистика прослушиваний** - модель Play, поле plays_count
6. ⬇️ **Скачивание треков** - поле downloads_allowed
7. 👥 **Подписки** - модель Follow
8. 🔒 **Приватные треки/плейлисты** - поле is_public

## Технологии

### Backend:
- Django 5.x
- SQLite (разработка) / PostgreSQL (продакшн)
- Pillow - обработка изображений
- mutagen - чтение метаданных аудио
- django-cleanup - автоудаление файлов

### Frontend:
- HTML/CSS/JavaScript
- Bootstrap 5
- Howler.js или HTML5 Audio API - аудиоплеер
- WaveSurfer.js - визуализация волны (опционально)

### Деплой (опционально):
- PythonAnywhere / Heroku / Render
- WhiteNoise - раздача статики
- Gunicorn - WSGI-сервер

## Структура проекта

```
soundcloudd/
├── manage.py
├── soundcloudd/          # Основной проект
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tracks/               # Приложение треков
│   ├── models.py         # Track, Comment, Like, Playlist, PlaylistTrack, Play, Genre
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/tracks/
├── users/                # Приложение пользователей
│   ├── models.py         # Profile, Follow
│   ├── views.py
│   ├── urls.py
│   └── templates/users/
├── media/                # Загруженные файлы
│   ├── tracks/
│   ├── covers/
│   ├── avatars/
│   └── playlists/
└── static/               # Статические файлы
    ├── css/
    ├── js/
    └── img/
```

## План разработки (6 дней)

1. **День 1**: Создание проекта, настройка моделей БД, миграции
2. **День 2**: Реализация авторизации и профилей
3. **День 3**: Загрузка и отображение треков, аудиоплеер
4. **День 4**: Комментарии, лайки, плейлисты
5. **День 5**: Поиск, жанры, подписки, стилизация
6. **День 6**: Тестирование, деплой (опционально), презентация

## Контакты

Если возникнут вопросы по диаграмме, обратитесь к преподавателю для утверждения.

---

*Учебная практика 2026*
