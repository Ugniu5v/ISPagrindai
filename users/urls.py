from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    # path("create/", views.createUser, name="createConcert"),
    # path("edit/", views.editUser, name="editConcert"),
    path("detail/<int:user_id>", views.userDetail, name="userDetail"),
    path("logout/", views.logoutUser, name="userLogout"),
]
