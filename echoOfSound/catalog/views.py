from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Track, Genre, Playlist, Profile, Comment
from .forms import TrackUploadForm


def home(request):
    """Главная страница"""
    popular_tracks = Track.objects.filter(is_public=True).order_by('-plays_count')[:6]
    genres = Genre.objects.all()[:5]

    context = {
        'popular_tracks': popular_tracks,
        'genres': genres,
    }
    return render(request, 'catalog/home.html', context)


class TrackListView(ListView):
    """Список всех треков (CBV)"""
    model = Track
    template_name = 'catalog/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        queryset = Track.objects.filter(is_public=True).select_related('author', 'genre').order_by('-created_at')

        # Поиск
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )

        # Фильтр по жанру
        genre_id = self.request.GET.get('genre', '')
        if genre_id:
            queryset = queryset.filter(genre_id=genre_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context


# Для обратной совместимости с URL
track_list = TrackListView.as_view()


def track_detail(request, slug):
    """Детальная страница трека"""
    track = get_object_or_404(Track, slug=slug)
    comments = track.comments.select_related('user').order_by('-created_at')

    # Обработка добавления комментария
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text')
        timestamp = request.POST.get('timestamp')

        if text:
            comment = Comment.objects.create(
                track=track,
                user=request.user,
                text=text,
                timestamp=int(timestamp) if timestamp else None
            )
            messages.success(request, 'Комментарий добавлен!')
            return redirect('track_detail', slug=slug)

    context = {
        'track': track,
        'comments': comments,
    }
    return render(request, 'catalog/track_detail.html', context)


class GenreListView(ListView):
    """Список жанров (CBV)"""
    model = Genre
    template_name = 'catalog/genre_list.html'
    context_object_name = 'genres'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Жанры'
        return context


genre_list = GenreListView.as_view()


class GenreDetailView(DetailView):
    """Детальная страница жанра (CBV)"""
    model = Genre
    template_name = 'catalog/genre_detail.html'
    context_object_name = 'genre'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Жанр: {self.object.name}"
        return context


genre_detail = GenreDetailView.as_view()


class PlaylistListView(ListView):
    """Список плейлистов (CBV)"""
    model = Playlist
    template_name = 'catalog/playlist_list.html'
    context_object_name = 'playlists'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Плейлисты'
        return context


playlist_list = PlaylistListView.as_view()


class PlaylistDetailView(DetailView):
    """Детальная страница плейлиста (CBV)"""
    model = Playlist
    template_name = 'catalog/playlist_detail.html'
    context_object_name = 'playlist'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = getattr(self.object, 'title', 'Плейлист')
        return context


playlist_detail = PlaylistDetailView.as_view()


def profile(request, username):
    """Профиль пользователя"""
    profile_obj = get_object_or_404(Profile, user__username=username)
    user_tracks = Track.objects.filter(author=profile_obj.user, is_public=True)[:6]

    context = {
        'profile': profile_obj,
        'user_tracks': user_tracks,
        'title': f"{profile_obj.user.username} — echoOfSound",
    }
    return render(request, 'catalog/profile.html', context)


@login_required
def my_profile(request):
    """Профиль текущего пользователя"""
    return profile(request, request.user.username)


def search(request):
    """Поиск треков"""
    query = request.GET.get('q', '')
    tracks = []
    if query:
        tracks = Track.objects.filter(
            is_public=True,
            title__icontains=query
        )[:20]

    context = {
        'tracks': tracks,
        'query': query,
        'title': 'Поиск',
    }
    return render(request, 'catalog/search.html', context)


# Авторизация
def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Валидация
        errors = []
        if not username or not password1 or not password2:
            errors.append('Все поля обязательны для заполнения')
        elif password1 != password2:
            errors.append('Пароли не совпадают')
        elif len(password1) < 8:
            errors.append('Пароль должен содержать минимум 8 символов')
        elif User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Создание пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')

    return render(request, 'catalog/register.html')


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'catalog/login.html')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def track_upload(request):
    """Загрузка трека"""
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.author = request.user

            # Генерируем slug из названия
            if not track.slug:
                from django.utils.text import slugify
                import uuid

                base_slug = slugify(track.title)

                # Если slug пустой (кириллица), используем uuid
                if not base_slug:
                    base_slug = f"track-{uuid.uuid4().hex[:8]}"

                # Проверяем уникальность slug
                slug = base_slug
                counter = 1
                while Track.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                track.slug = slug

            track.save()
            messages.success(request, f'Трек "{track.title}" успешно загружен!')
            return redirect('track_detail', slug=track.slug)
    else:
        form = TrackUploadForm()

    context = {
        'form': form,
        'title': 'Загрузить трек',
    }
    return render(request, 'catalog/track_upload.html', context)


@login_required
def track_delete(request, slug):
    """Удаление трека"""
    track = get_object_or_404(Track, slug=slug)

    # Проверяем, что пользователь является автором трека
    if track.author != request.user:
        messages.error(request, 'Вы не можете удалить чужой трек!')
        return redirect('track_detail', slug=slug)

    if request.method == 'POST':
        track_title = track.title
        track.delete()
        messages.success(request, f'Трек "{track_title}" успешно удалён!')
        return redirect('my_profile')

    context = {
        'track': track,
        'title': f'Удалить трек: {track.title}',
    }
    return render(request, 'catalog/track_delete.html', context)