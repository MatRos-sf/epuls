from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View

from ..models import FriendRequest, Profile, ProfileType


class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "account/friends.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        context["username"] = username
        context["self"] = self.request.user.username == username
        return context


def send_to_friends(request, username):
    obj, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=User.objects.get(username=username)
    )
    if created:
        messages.success(request, "Friend request sent!")
    else:
        messages.info(request, "Friend request was already sent!")

    return redirect("account:profile", username=username)


def unfriend(request, username):
    user_for_delete = get_object_or_404(User, username=username)
    request.user.profile.remove_friend(user_for_delete)
    return redirect("account:profile", username=user_for_delete)


class InvitesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "account/invite/list.html"

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def test_func(self):
        return self.request.user.username == self.kwargs.get("username")


def invite_accept(request, username, pk):
    instance = get_object_or_404(FriendRequest, pk=pk)
    if not instance.accept():
        messages.error(request, "You cannot accept this request!")
    instance.delete()

    return redirect("account:invites", username=username)


def invite_reject(request, username, pk):
    instance = get_object_or_404(FriendRequest, pk=pk)
    instance.delete()

    return redirect("account:invites", username=username)


class BestFriendsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Profile
    template_name = "account/bf_list.html"

    def get_queryset(self):
        owner = self.request.user
        return Profile.objects.get(user=owner).friends.all()

    def get_context_data(self, *args, **kwargs):
        """
        Extra context:
            * bf_list: list of pk who are best friends
        """
        context = super().get_context_data(*args, **kwargs)
        profile_instance = Profile.objects.get(user=self.request.user)
        bf = profile_instance.best_friends.values_list("pk", flat=True)

        context["bf_list"] = bf

        return context

    def test_func(self):
        return self.request.user.profile.type_of_profile != ProfileType.BASIC


class RemoveBestFriendsView(LoginRequiredMixin, UserPassesTestMixin, View):
    http_method_names = ["post"]

    def post(self, request, username, pk):
        """
        Removes best friends from user best friends list.
        """
        user_to_del = User.objects.get(pk=pk)
        request.user.profile.remove_best_friend(friend=user_to_del)
        messages.success(
            request, f"{user_to_del} has been removed for your best friends."
        )
        return redirect("account:best-friends", username=username)

    def test_func(self):
        login_user = self.request.user
        return self.kwargs.get("username") == login_user.username


class AddBestFriendsView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, username, pk):
        user_to_add = User.objects.get(pk=pk)
        try:
            request.user.profile.add_best_friend(friend=user_to_add)
        except ValidationError as e:
            print(e.messages)
            messages.error(request, e.messages[0])

        return redirect("account:best-friends", username=username)
