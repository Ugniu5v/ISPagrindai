from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:user_id>/", views.userDetail, name="userDetail"),
    path("edit/", views.userEdit, name="userEdit"),
    path("edit/twoFaURI", views.twoFaURI, name="twoFaURI"),
    path("logout/", views.logoutUser, name="userLogout"),
    path("login/", views.loginUser, name="userLogin"),
    path("register/", views.registerUser, name="userRegister"),
    path("admin/", views.admin, name="admin"), # type: ignore
    path("admin/users/", views.adminUsers, name="adminUsers"), # type: ignore
]
