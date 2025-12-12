from django.urls import path
from . import views

app_name = "playlists"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createPlaylist, name="createPlaylist"),
    path("<int:pk>/", views.PlaylistDetail, name="PlaylistDetail"),
    path("<int:pk>/edit/", views.editPlaylist, name="editPlaylist"),
    path("<int:pk>/delete/", views.deletePlaylist, name="deletePlaylist"),
    path("<int:grojarastis_id>/remove/<int:song_id>/", 
     views.deleteFromPlaylist, 
     name="deleteFromPlaylist"),
    path("<int:pk>/play/<int:song_id>/", views.playPlaylistSong, name="playPlaylistSong"),
]