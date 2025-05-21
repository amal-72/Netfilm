from django.contrib import admin
from .models import Movie, MovieList, Section, Profile

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_date', 'movie_views')
    search_fields = ('title', 'genre')
    list_filter = ('genre', 'release_date')

class MovieListAdmin(admin.ModelAdmin):
    list_display = ('owner_user', 'movie', 'date_added')
    search_fields = ('owner_user__username', 'movie__title')
    list_filter = ('date_added',)

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    filter_horizontal = ('movies',)
    list_filter = ('is_active',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_child', 'created_at')
    list_filter = ('is_child', 'created_at')
    search_fields = ('user__username', 'name')

admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieList, MovieListAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Profile, ProfileAdmin)