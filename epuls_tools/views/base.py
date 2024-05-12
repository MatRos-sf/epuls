from typing import Any

from django.contrib.auth.models import User
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from notifications.signals import notify

from .tracker import EpulsTracker


class EpulsBaseView(EpulsTracker):
    """Handles a basic view of custom view."""

    def send_notification(
        self, actor: User, recipient: User, verb: str, act_obj: Any, **kwargs
    ):
        """Creates notification."""
        notify.send(
            sender=actor,
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=act_obj,
            **kwargs
        )

    def get(self, request, *args, **kwargs) -> Any:
        """
        Overwrite method and add tracker system.
        """
        response = super().get(request, *args, **kwargs)
        self.tracker()
        return response


class EpulsDetailView(EpulsBaseView, DetailView):
    """
    Render a "detail" view of an object and tracking user actions.
    """


class EpulsListView(EpulsBaseView, ListView):
    """Render a list of objects and tracking user actions."""


class EpulsCreateView(EpulsBaseView, CreateView):
    """View for creating a new object, with a response rendered by a template and tracking user's action."""


class EpulsUpdateView(EpulsBaseView, UpdateView):
    """View for updating an object and tracking user's action."""


class EpulsDeleteView(EpulsBaseView, DeleteView):
    """View for deleting an object and tracking user's action."""
