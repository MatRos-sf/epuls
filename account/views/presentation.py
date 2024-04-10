from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from account.forms import PresentationForm
from account.models import Profile


class PresentationUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = PresentationForm
    template_name = "account/form_presentation.html"
    extra_context = {"button": "Save"}

    def get_object(self, queryset=None):
        user = self.request.user
        return get_object_or_404(Profile, user=user)
