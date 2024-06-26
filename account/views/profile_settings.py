from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from account.forms import AboutUserForm, ChangeUsernameForm, ProfileForm
from account.models import AboutUser, Profile, ProfileType
from epuls_tools.scaler import give_away_puls
from puls.models import PulsType, SinglePuls


class UserSettings(UserPassesTestMixin):
    def test_func(self):
        instance = self.get_object()
        user = self.request.user
        if isinstance(instance, Profile):
            return instance.user == user

        return instance == user


class ProfileUpdateView(LoginRequiredMixin, UserSettings, UpdateView):
    template_name = "account/forms.html"
    model = Profile
    form_class = ProfileForm
    extra_context = {"title": "Update Profile", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        profile = self.get_object()
        return reverse("account:profile", kwargs={"username": profile.user.username})


def check_is_value_set(puls_instance, model_attr: str) -> bool:
    """
    Checks that attr is set or attr is waiting for accepted in SinglePuls.
    """
    value = getattr(puls_instance, model_attr)
    is_pulses = SinglePuls.objects.filter(
        puls=puls_instance,
        type=getattr(PulsType, model_attr.upper()),
        is_accepted=False,
    ).exists()

    return value or is_pulses


class AboutUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(AboutUser, profile__user=self.request.user)

    def get_success_url(self):
        instance_owner = self.get_object().profile
        self.__give_puls(instance_owner, "about_me")
        return reverse(
            "account:profile", kwargs={"username": instance_owner.user.username}
        )

    def test_func(self):
        instance_owner = self.get_object().profile.user
        return instance_owner == self.request.user

    def __give_puls(self, model: Profile, name_attr: str) -> None:
        instance = getattr(model, name_attr)
        if not instance.is_set:
            if instance.check_model_is_fill_up():
                give_away_puls(user_profile=model, type="about_me")


class SettingsTemplateView(TemplateView):
    template_name = "account/settings.html"


class UserNameChangeView(LoginRequiredMixin, UpdateView):
    form_class = ChangeUsernameForm
    template_name = "account/base/basic_form.html"
    extra_context = {"title": "Username Change", "action": "Save"}
    success_url = reverse_lazy("account:settings")

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        # TODO $ -> in get_succes_url we should take $
        if self.request.user.profile.type_of_profile == ProfileType.BASIC:
            messages.error(
                self.request,
                "Your profile type is BASIC, you are not allowed to change your username.",
            )
            return HttpResponseRedirect(self.get_success_url())

        return super().form_valid(form)
