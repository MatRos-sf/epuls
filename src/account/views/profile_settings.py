from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import UpdateView

from account.forms import AboutUserForm, ProfileForm
from account.models import AboutUser, Profile


class UserSettings(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = Profile
    form_class = ProfileForm
    extra_context = {"title": "Update Profile", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        user = self.get_object()
        return reverse("account:profile", kwargs={"username": user.username})

    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )


class AboutUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        return self.get_object()

    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )

    # TODO tutaj będzie sprawdzać czy wszystkie pola są uzupełnione jak nie to wpisuje punkty
