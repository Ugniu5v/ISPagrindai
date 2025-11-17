from django.db import models


class MyUser(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password_hash = models.CharField(max_length=50)
    role = models.SmallIntegerField()
    display_name = models.CharField(max_length=50)
    biography = models.TextField()
    profile_cover_url = models.ImageField()
    profile_cover_small_url = models.ImageField()
    two_factor_enabled = models.BooleanField()
    two_factor_method = models.IntegerField()
    two_factor_secret = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField()
    is_active = models.BooleanField()
    is_public = models.BooleanField()
    date_of_birth = models.DateField()
