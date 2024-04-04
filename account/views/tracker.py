from enum import StrEnum
from typing import Optional

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from action.models import Action, ActionMessage


def validate_view_inheritance(method):
    def wrapper(self, *args, **kwargs):
        if not issubclass(self.__class__, View):
            raise ImproperlyConfigured(
                f"Class {self.__class__.__name__} must be subclass of django.views.View"
            )
        return method(self, *args, **kwargs)

    return wrapper


class ActionType(StrEnum):
    PROFILE = "PROFILE"


class EpulsTracker:
    activity = None

    @validate_view_inheritance
    def action(self) -> None:
        """
        Track user activity and create or update Action models.
        If the last recorded Action from the user is the same as the current activity, only update the date field
        of the last action. Unless the last Action is different or there's no previous action then create new one.

        """
        if self.activity is None:
            raise ImproperlyConfigured("activity field must be set before action")
        username = self.kwargs.get("username")
        is_owner = self.request.user.username == username

        whom = None if is_owner else get_object_or_404(User, username=username)

        action = self.get_action_message(self.activity, is_owner)

        last_action = Action.objects.filter(who=self.request.user).first()

        # create or update Action
        if last_action.action == action:
            last_action.date = timezone.now()
            last_action.save(update_fields=["date"])
        else:
            Action.objects.create(who=self.request.user, whom=whom, action=action)

    @validate_view_inheritance
    def get_username_from_url(self) -> Optional[str]:
        return self.kwargs.get("username", None)

    @staticmethod
    def get_action_message(activity: str, is_owner: bool) -> str:
        return (
            getattr(ActionMessage, f"OWN_{activity}")
            if is_owner
            else getattr(ActionMessage, f"SB_{activity}")
        )
