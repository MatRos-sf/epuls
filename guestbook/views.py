from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from epuls_tools.scaler import give_away_puls
from epuls_tools.views import ActionType, EpulsListView
from puls.models import PulsType

from .forms import GuestbookUserForm
from .models import Guestbook


class GuestbookView(LoginRequiredMixin, EpulsListView):
    template_name = "guestbook/guestbook.html"
    model = Guestbook
    extra_context = {"form": GuestbookUserForm}
    activity = ActionType.GUESTBOOK

    def get_queryset(self) -> Any:
        return Guestbook.objects.filter(receiver=self.get_user())

    def post(self, request, *args, **kwargs) -> Any:
        """
        Handles POST request to create an entry in the Guestbook.

        If the user has not already created an entry in the Guestbook, this method create one.
        If the entry is successfully created, the user's will get a puls.
        """

        form = GuestbookUserForm(request.POST)

        if form.is_valid():
            receiver = self.get_user()
            instance = form.save(commit=False)

            sender = self.get_login_user()

            # create entry and give puls
            if self.check_permission_entry(sender, receiver):
                instance.sender = sender
                instance.receiver = receiver
                instance.save()

                give_away_puls(user_profile=sender.profile, type=PulsType.GUESTBOOKS)

                messages.success(request, "An entry has been added!")

            else:
                messages.error(request, "You have created a entry for this guestbook.")

        return self.get(request, *args, **kwargs)

    def check_permission_entry(self, sender: User, receiver: User) -> bool:
        """The method returns True if sender hasn't created any guestbook entry for receiver."""
        return (
            not self.check_users()
            and not Guestbook.objects.filter(sender=sender, receiver=receiver).exists()
        )

    def get_context_data(self, **kwargs):
        """
        Extra context:
            * self (bool) -> is user's gurstbook
        """
        context = super(GuestbookView, self).get_context_data(**kwargs)
        context["self"] = self.check_users()
        return context
