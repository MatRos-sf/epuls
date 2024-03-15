from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from account.forms import GuestbookUserForm, UserSignupForm
from account.models import Guestbook
from puls.models import PulsType
from puls.scaler import give_away_puls


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


class GuestbookView(LoginRequiredMixin, ListView):
    template_name = "account/guestbook/guestbook.html"
    model = Guestbook
    extra_context = {"form": GuestbookUserForm}

    def get_queryset(self) -> Any:
        username = self.kwargs.get("username")
        return Guestbook.objects.filter(receiver__username=username)

    def post(self, request, *args, **kwargs) -> Any:
        form = GuestbookUserForm(request.POST)

        if form.is_valid():
            username = self.__get_username_from_url()
            instance = form.save(commit=False)
            instance.sender = self.request.user
            instance.receiver = User.objects.get(username=username)
            instance.save()
            # TODO: 1 entry
            messages.success(request, "An entry has been added!")
            give_away_puls(
                user_profile=self.request.user.profile, type=PulsType.GUESTBOOKS
            )

        return self.get(request, *args, **kwargs)

    def __get_username_from_url(self) -> str:
        return self.kwargs.get("username")

    def get_context_data(self, **kwargs):
        context = super(GuestbookView, self).get_context_data(**kwargs)

        context["self"] = self.request.user.username == self.__get_username_from_url()
        print(context)
        return context
