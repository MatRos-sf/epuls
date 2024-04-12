from enum import StrEnum, auto

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .tracker import EpulsTracker


class EpulsDetailView(EpulsTracker, DetailView):
    """
    Render a "detail" view of an object and tracking user actions.
    """


class EpulsListView(EpulsTracker, ListView):
    """Render a list of objects and tracking user actions."""


class EpulsCreateView(EpulsTracker, CreateView):
    """View for creating a new object, with a response rendered by a template and tracking user's action."""


class EpulsUpdateView(EpulsTracker, UpdateView):
    """View for updating an object and tracking user's action."""


class EpulsDeleteView(EpulsTracker, DeleteView):
    """View for deleting an object and tracking user's action."""
