from django.urls import path
from . import views

app_name = "playlists"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createPlaylist, name="createPlaylist"),
    path("<int:pk>/", views.PlaylistDetail, name="PlaylistDetail"),
    path("<int:pk>/edit/", views.editPlaylist, name="editPlaylist"),
]
