from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from account.forms import GuestbookUserForm, UserSignupForm
from account.models import Guestbook, Profile, Visitor
from action.models import Action, ActionMessage
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


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "account/profile.html"

    def __get_user_for_path(self):
        return self.kwargs.get("username", None)

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        user_instance = get_object_or_404(User, username=username)
        if user_instance != self.request.user.username:
            # user is Visitor
            Visitor.objects.create(visitor=self.request.user, receiver=user_instance)
        return user_instance

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context["action"] = Action.objects.filter(
            who__username=self.__get_user_for_path()
        ).first()
        return context

    def __action(self, activity: str = "PROFILE") -> None:
        username = self.kwargs.get("username")
        whom = User.objects.get(username=username)
        is_own_action = self.request.user == whom
        if is_own_action:
            whom = None
        action = (
            getattr(ActionMessage, f"OWN_{activity}")
            if is_own_action
            else getattr(ActionMessage, f"SB_{activity}")
        )

        last_action = Action.objects.filter(who=self.request.user).first()

        if not last_action:
            Action.objects.create(who=self.request.user, action=action, whom=whom)
        elif last_action.action == action:
            last_action.date = timezone.now()
            last_action.save(update_fields=["date"])
        else:
            Action.objects.create(who=self.request.user, whom=whom, action=action)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        self.__action()

        return self.render_to_response(context)


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

        return context


class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "account/friends.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()
