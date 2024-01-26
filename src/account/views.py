# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from .forms import UserSignupForm
from .models import Profile, Visitor


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
