from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import FormView

from epuls_tools.expections import NotRunToUse, ValidationError

from .forms import ShouterForm
from .models import Shouter


class ShouterCreateView(LoginRequiredMixin, FormView):
    model = Shouter
    form_class = ShouterForm
    template_name = "account/base/basic_form.html"
    success_url = reverse_lazy("shouter:create")
    extra_context = {"title": "Create Shouter"}

    def __create_shouter(self, text: str, time: int):
        """Create a new Shouter model"""
        time_now = timezone.now()

        Shouter.objects.create(
            user=self.request.user,
            text=text,
            created=time_now,
            expiration=time_now + timedelta(hours=time),
        )

    def form_valid(self, form):
        """Capture data and create new Shouter model"""
        data_form = form.cleaned_data
        text = data_form.get("shouter")
        time = int(data_form.get("time"))

        # TODO: conditoinal self.request.user.profile.check_pulsars() which check than user has enough pulsars to post shouter

        # create Shouter
        self.__create_shouter(text, time)

        return super().form_valid(form)
