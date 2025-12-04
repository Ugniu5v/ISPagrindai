from django import forms
from django.core.exceptions import ValidationError
from users.models import User


class LoginForm(forms.Form):
    password1 = forms.CharField(label="Slaptažodis", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Slaptažodžio pakartojimas", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "email", "date_of_birth", "display_name")

    # def clean_password2(self):
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise ValidationError("Slaptažodžiai nėra vienodi")
    #     return password2

    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #     return user
