from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator




class User(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "Admin", "Administratorius"
        REGISTERED = "Registered", "Registruotas naudotojas"

    username = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(5, "Turi būti bent 5 simboliai"),
            MaxLengthValidator(50, "Turi būti ne daugiau nei 50 simbolių"),
        ],
        editable=False
    )
    email = models.EmailField(max_length=254)
    password_hash = models.BinaryField(max_length=60)
    role = models.CharField(max_length=10, choices=RoleChoices, default=RoleChoices.REGISTERED)
    display_name = models.CharField(max_length=50)
    biography = models.TextField(blank=True, null=True)
    profile_cover_url = models.ImageField(blank=True, null=True, upload_to="profile_covers")
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_login_at = models.DateTimeField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return self.username


class Following(models.Model):
    class FollowingChoices(models.TextChoices):
        ACTIVE = "A", "Aktyvus"
        BLOCKED = "B", "Užblokuotas"
        SILENCED = "S", "Nutildytas"

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    date = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=1, choices=FollowingChoices)

    def __str__(self) -> str:
        return f"State: {self.state}"

class TwoFaCodeCopy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="twoFaSecrets") 
    code_hash = models.BinaryField(max_length=60)
    time_created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self) -> str:
        return f"User: {self.user.display_name}, Created: {self.time_created}, Code hash: {self.code_hash}"