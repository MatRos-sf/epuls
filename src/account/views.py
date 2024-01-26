# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, UpdateView

from .forms import AboutUserForm, ProfileForm, UserSignupForm
from .models import AboutUser, Profile, Visitor


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class ProfileView(DetailView):
    model = Profile
    template_name = "account/profile.html"
    slug_field = "username"  # TODO ?
    slug_url_kwarg = "username"  # TODO ?

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        user_instance = get_object_or_404(User, username=username)
        if user_instance != self.request.user.username:
            # user is Visitor
            Visitor.objects.create(visitor=self.request.user, receiver=user_instance)
        return user_instance


class ProfileUpdateView(UpdateView):
    template_name = "account/forms.html"
    model = Profile
    slug_field = "username"
    slug_url_kwarg = "username"
    form_class = ProfileForm
    extra_context = {"title": "Update Profile"}

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        return get_object_or_404(User, username=username)


class AboutUserView(UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User"}

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        return get_object_or_404(User, username=username)
