from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator


class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "Admin", "Administratorius"
        REGISTERED = "Registered", "Registruotas naudotojas"
        GUEST = "Guest", "Naudotojas"

    username = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(5, "Turi būti bent 5 simboliai"),
            MaxLengthValidator(50, "Turi būti ne daugiau nei 50 simbolių"),
        ],
    )
    email = models.EmailField(max_length=254)
    password_hash = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=RoleChoices)
    display_name = models.CharField(max_length=50)
    biography = models.TextField()
    profile_cover_url = models.ImageField(null=True)
    profile_cover_small_url = models.ImageField(null=True)
    two_factor_enabled = models.BooleanField()
    two_factor_method = models.IntegerField()
    two_factor_secret = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField()
    is_active = models.BooleanField()
    is_public = models.BooleanField()
    date_of_birth = models.DateField()

    def __str__(self) -> str:
        return self.username


# class FallowingState(models.Model):
#     pass


class Fallowing(models.Model):
    class FallowingChoices(models.TextChoices):
        ACTIVE = "A", "Aktyvus"
        BLOCKED = "B", "Užblokuotas"
        SILENCED = "S", "Nutildytas"

    fallower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fallowing"
    )
    fallowed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fallowers"
    )
    date = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=1, choices=FallowingChoices)

    def __str__(self) -> str:
        return f"State: {self.state}"
