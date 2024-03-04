from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import UpdateView

from account.forms import AboutUserForm, ProfileForm
from account.models import AboutUser, Profile
from puls.models import PulsType, SinglePuls
from puls.scaler import scale_puls


class UserSettings(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().username == self.request.user.username


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
        if instance.is_set():
            if not model.puls.check_is_value_set(name_attr):
                puls_type = getattr(PulsType, name_attr.upper())
                qnt = scale_puls(puls_type)

                SinglePuls.objects.create(puls=model.puls, type=puls_type, quantity=qnt)
