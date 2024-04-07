from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from account.forms import GuestbookUserForm, UserSignupForm
from account.models import Guestbook
from puls.models import PulsType
from puls.scaler import give_away_puls

from .base import ActionType, EpulsListView


class HomeView(View):
    # TODO: login here
    def get(self, request):
        recently_login_users = User.objects.all().order_by("-last_login")[:5]

        # TODO: recently_login_women, recently_login_man, rag 3
        new_users = User.objects.all().order_by("-date_joined")[:5]

        context = {"recently_login_users": recently_login_users, "new_users": new_users}

        return render(request, "account/home.html", context)


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            gender = form.cleaned_data.pop("gender")
            instance = form.save()
            # set a gender
            profile = instance.profile
            profile.gender = gender
            profile.save()

            return redirect("account:login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class GuestbookView(LoginRequiredMixin, EpulsListView):
    template_name = "account/guestbook/guestbook.html"
    model = Guestbook
    extra_context = {"form": GuestbookUserForm}
    activity = ActionType.GUESTBOOK

    def get_queryset(self) -> Any:
        username = self.__get_username_from_url()
        return Guestbook.objects.filter(receiver__username=username)

    def post(self, request, *args, **kwargs) -> Any:
        form = GuestbookUserForm(request.POST)

        if form.is_valid():
            username = self.__get_username_from_url()
            instance = form.save(commit=False)

            sender = self.request.user
            receiver = User.objects.get(username=username)

            # create entry and give puls
            if self.check_permission_entry(sender, receiver):
                instance.sender = self.request.user
                instance.receiver = User.objects.get(username=username)
                instance.save()

                give_away_puls(user_profile=sender.profile, type=PulsType.GUESTBOOKS)

                messages.success(request, "An entry has been added!")

            else:
                messages.error(request, "You have created a entry for this guestbook.")

        return self.get(request, *args, **kwargs)

    def check_permission_entry(self, sender: User, receiver: User) -> bool:
        """The method returns True if sender hasn't created any guestbook entry for receiver."""
        return (
            sender != receiver
            and not Guestbook.objects.filter(sender=sender, receiver=receiver).exists()
        )

    def __get_username_from_url(self) -> str:
        return self.kwargs.get("username")

    def get_context_data(self, **kwargs):
        context = super(GuestbookView, self).get_context_data(**kwargs)
        context["self"] = self.request.user.username == self.__get_username_from_url()
        return context


class UserListView(ListView):
    model = User
    template_name = "account/user_list.html"

    def get_queryset(self):
        q = self.request.GET.get("q", None)
        if q:
            return User.objects.filter(username__icontains=q)
        return User.objects.all()
