from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Треки
    path('tracks/', views.track_list, name='track_list'),
    path('tracks/<slug:slug>/', views.track_detail, name='track_detail'),
    path('upload/', views.track_upload, name='track_upload'),
    path('tracks/<slug:slug>/delete/', views.track_delete, name='track_delete'),

    path('profile/<str:username>/', views.profile, name='profile'),
    path('my-profile/', views.my_profile, name='my_profile'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genre/<slug:slug>/', views.genre_detail, name='genre_detail'),

    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlist/<slug:slug>/', views.playlist_detail, name='playlist_detail'),

    path('search/', views.search, name='search'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]