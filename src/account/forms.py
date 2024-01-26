from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import AboutUser, Profile


class UserSignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "date_of_birth",
            "short_description",
        )


class AboutUserForm(forms.ModelForm):
    class Meta:
        model = AboutUser
        fields = "__all__"
