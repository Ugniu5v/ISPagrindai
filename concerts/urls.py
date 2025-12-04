from django.urls import path, include
from . import views

app_name = "concerts"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.createConcert, name="createConcert"),
    path("<int:pk>/edit/", views.editConcert, name="editConcert"),
    path("search/", views.searchConcert, name="searchConcert"),
    path("<int:pk>", views.concertDetail, name="concertDetail"),
    path("recommendation/", views.recommendationConcert, name="recommendationConcert"),
]
