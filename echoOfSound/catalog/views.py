from django.shortcuts import render
from .models import Profile
from django.contrib.auth.models import User
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile  # благодаря OneToOneField
    return render(request, 'catalog/profile.html', {'profile': profile})
# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Track, Genre, Playlist, Profile


def home(request):
    """Главная страница"""
    latest_tracks = Track.objects.filter(is_public=True).order_by('-created_at')[:6]
    genres = Genre.objects.all()[:5]

    context = {
        'latest_tracks': latest_tracks,
        'genres': genres,
        'title': 'echoOfSound — Дом тёмной музыки',
    }
    return render(request, 'catalog/home.html', context)


def track_list(request):
    """Список всех треков"""
    tracks = Track.objects.filter(is_public=True).order_by('-created_at')
    context = {
        'tracks': tracks,
        'title': 'Все треки',
    }
    return render(request, 'catalog/track_list.html', context)


def track_detail(request, slug):
    """Детальная страница трека"""
    track = get_object_or_404(Track, slug=slug)
    context = {
        'track': track,
        'title': track.title,
    }
    return render(request, 'catalog/track_detail.html', context)


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


def genre_list(request):
    """Список жанров"""
    genres = Genre.objects.all()
    context = {
        'genres': genres,
        'title': 'Жанры',
    }
    return render(request, 'catalog/genre_list.html', context)


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