from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        profile = self.get_object()
        return reverse("account:profile", kwargs={"username": profile.user.username})

    def test_func(self):
        return self.get_object().user == self.request.user

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )


class AboutUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(AboutUser, profile__user=self.request.user)

    def get_success_url(self):
        instance_owner = self.get_object().profile.user.username
        return reverse("account:profile", kwargs={"username": instance_owner})

    def test_func(self):
        instance_owner = self.get_object().profile.user
        return instance_owner == self.request.user

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )

    # TODO tutaj będzie sprawdzać czy wszystkie pola są uzupełnione jak nie to wpisuje punkty
