from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.shortcuts import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    get_object_or_404,
    redirect,
)
from django.views.generic import ListView, View

from ..mixins import NotBasicTypeMixin, UsernameMatchesMixin
from ..models import FriendRequest, Profile
from .base import ActionType, EpulsListView


class FriendsListView(LoginRequiredMixin, EpulsListView):
    template_name = "account/friends.html"
    activity = ActionType.FRIENDS

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        context["username"] = username
        context["self"] = self.request.user.username == username
        return context


def send_to_friends(
    request, username
) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
    obj, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=User.objects.get(username=username)
    )
    if created:
        messages.success(request, "Friend request sent!")
    else:
        messages.info(request, "Friend request was already sent!")

    return redirect("account:profile", username=username)


def unfriend(request, username) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
    user_for_delete = get_object_or_404(User, username=username)
    request.user.profile.remove_friend(user_for_delete)
    return redirect("account:profile", username=user_for_delete)


class InvitesListView(LoginRequiredMixin, UsernameMatchesMixin, ListView):
    template_name = "account/invite/list.html"

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)


def invite_accept(
    request, username, pk
) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
    instance = get_object_or_404(FriendRequest, pk=pk)
    if not instance.accept():
        messages.error(request, "You cannot accept this request!")
    instance.delete()

    return redirect("account:invites", username=username)


def invite_reject(
    request, username, pk
) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
    instance = get_object_or_404(FriendRequest, pk=pk)
    instance.delete()

    return redirect("account:invites", username=username)


class BestFriendsListView(LoginRequiredMixin, NotBasicTypeMixin, ListView):
    model = Profile
    template_name = "account/bf_list.html"

    def get_queryset(self):
        owner = self.request.user
        return Profile.objects.get(user=owner).friends.all()

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Extra context:
            * bf_list: list of pk who are best friends
        """
        context = super().get_context_data(*args, **kwargs)
        profile_instance = Profile.objects.get(user=self.request.user)
        bf = profile_instance.best_friends.values_list("pk", flat=True)

        context["bf_list"] = bf

        return context


class RemoveBestFriendsView(LoginRequiredMixin, NotBasicTypeMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
        """
        Removes best friends from user best friends list.
        """
        user_to_del = get_object_or_404(User, pk=pk)
        request.user.profile.remove_best_friend(friend=user_to_del)
        messages.success(
            request, f"{user_to_del} has been removed for your best friends."
        )
        return redirect("account:best-friends")


class AddBestFriendsView(LoginRequiredMixin, NotBasicTypeMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk) -> HttpResponsePermanentRedirect | HttpResponseRedirect:
        """
        Adds new best friend to the user best friends list when pass all conditionals.
        """
        user_to_add = get_object_or_404(User, pk=pk)
        try:
            request.user.profile.add_best_friend(friend=user_to_add)
            messages.success(
                request, f"{user_to_add} has been added to your best friends list."
            )
        except ValidationError as e:
            messages.error(request, e.messages[0])

        return redirect("account:best-friends")
