from django.urls import path
from . import views

app_name = "playlists"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createPlaylist, name="createPlaylist"),
    path("search/", views.searchPlaylist, name="searchPlaylist"),
    path("detail/<int:playlist_id>/", views.playlistDetail, name="playlistDetail"),
    path("edit/<int:playlist_id>/", views.editPlaylist, name="editPlaylist"),
]
