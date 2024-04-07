from enum import StrEnum

from django.views.generic import DetailView

from .tracker import EpulsTracker


class ActionType(StrEnum):
    PROFILE = "PROFILE"


class EpulsDetailView(DetailView, EpulsTracker):
    """
    Custom DetailView
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # track user action
        self.tracker()

        return self.render_to_response(context)
