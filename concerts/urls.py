from django.urls import path, include
from . import views

app_name = "concerts"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createConcert, name="createConcert"),
    path("edit/", views.editConcert, name="editConcert"),
    path("search/", views.searchConcert, name="searchConcert"),
]
