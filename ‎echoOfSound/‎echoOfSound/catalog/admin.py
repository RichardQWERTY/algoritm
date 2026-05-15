from django.contrib import admin
from .models import Profile, Genre, Track, Comment, Like, Playlist, PlaylistTrack, Follow, Play

# Промежуточная таблица для добавления треков прямо внутри плейлиста в админке
class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'location')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)} # Слаг генерируется автоматически из названия

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'plays_count', 'is_public', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('genre', 'is_public')
    search_fields = ('title', 'author__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('track', 'user', 'timestamp', 'created_at')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('track', 'user', 'created_at')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlaylistTrackInline]

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')

@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('track', 'user', 'ip_address', 'played_at')