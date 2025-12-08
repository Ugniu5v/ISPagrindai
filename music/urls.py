from django.urls import path
from . import views

app_name = "music"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createSong, name="createSong"),
    path("rate/", views.rateSong, name="rateSong"),
    path("edit/", views.editSong, name="editSong"),
    path("play/<int:song_id>", views.playSong, name="playSong"),
    path("similar/", views.similarSongs, name="similarSongs"),
    path("add/<int:song_id>/", views.addToPlaylist, name="addToPlaylist"),
]
