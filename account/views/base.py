from enum import StrEnum, auto

from django.views.generic import DetailView, ListView

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


class EpulsDetailView(DetailView, EpulsTracker):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.tracker()
        return response


class EpulsListView(ListView, EpulsTracker):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.tracker()
        return response
