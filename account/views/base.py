from enum import StrEnum, auto

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .tracker import EpulsTracker

__all__ = ["ActionType", "EpulsDetailView", "EpulsListView"]


class ActionType(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    PROFILE = auto()
    GUESTBOOK = auto()
    DIARY = auto()
    FRIENDS = auto()
    GALLERY = auto()
    PULS = auto()


class EpulsDetailView(EpulsTracker, DetailView):
    """
    Render a "detail" view of an object and tracking user actions.
    """


class EpulsListView(EpulsTracker, ListView):
    """Render a list of objects and tracking user actions."""


class EpulsCreateView(EpulsListView, CreateView):
    """View for creating a new object, with a response rendered by a template and tracking user's action."""


class EpulsUpdateView(EpulsTracker, UpdateView):
    """View for updating an object and tracking user's action."""


class EpulsDeleteView(EpulsTracker, DeleteView):
    """View for deleting an object and tracking user's action."""
