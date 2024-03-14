from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from ..models import FriendRequest


class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "account/friends.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()


def send_to_friends(request, username):
    obj, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=User.objects.get(username=username)
    )
    if created:
        messages.success(request, "Friend request sent!")
    else:
        messages.info(request, "Friend request was already sent!")

    return redirect("account:profile", username=username)


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
