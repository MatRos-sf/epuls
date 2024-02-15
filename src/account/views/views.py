from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from account.forms import GuestbookUserForm, UserSignupForm
from account.models import Guestbook, Profile, Visitor


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "account/profile.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        user_instance = get_object_or_404(User, username=username)
        if user_instance != self.request.user.username:
            # user is Visitor
            Visitor.objects.create(visitor=self.request.user, receiver=user_instance)
        return user_instance


class GuestbookView(LoginRequiredMixin, ListView):
    template_name = "account/guestbook.html"
    model = Guestbook
    extra_context = {"form": GuestbookUserForm}

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Guestbook.objects.filter(receiver__username=username)

    def post(self, request, *args, **kwargs):
        form = GuestbookUserForm(request.POST)
        if form.is_valid():
            username = self.kwargs.get("username")
            instance = form.save(commit=False)
            instance.sender = self.request.user
            instance.receiver = User.objects.get(username=username)
            instance.save()

        return self.get(request, *args, **kwargs)


class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "account/friends.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()
