from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from account.models import Visitor
from action.models import Action, ActionMessage


def validate_view_inheritance(method):
    def wrapper(self, *args, **kwargs):
        if not issubclass(self.__class__, View):
            raise ImproperlyConfigured(
                f"Class {self.__class__.__name__} must be subclass of django.views.View"
            )
        return method(self, *args, **kwargs)

    return wrapper


class EpulsTracker:
    activity = None

    def action(self, *, login_user: User, whom, is_current) -> None:
        """
        Track user activity and create or update Action models.
        If the last recorded Action from the user is the same as the current activity, only update the date field
        of the last action. Unless the last Action is different or there's no previous action then create new one.
        """
        action = self.get_action_message(self.activity, is_current)

        last_action = Action.last_user_action(who=login_user)

        # create or update Action
        if last_action and last_action.action == action:
            last_action.date = timezone.now()
            last_action.save(update_fields=["date"])
        else:
            Action.objects.create(who=login_user, whom=whom, action=action)

    def visitor(self, whom: User, login_user: User) -> None:
        """
        Creates a visitor who visits the profile of someone and updates the 'male_visitor' or 'female_visitor' field
        depending on the gender of the visiting user.
        Parameters:
            - whom (User): The user whose profile is being visited.
            - login_user (User): The user who is visiting the profile.
        """
        Visitor.objects.create(visitor=login_user, receiver=whom)

        gender = login_user.profile.get_gender_display().lower()

        # add gender to the counter
        whom.profile.add_visitor(gender)

    @validate_view_inheritance
    def tracker(self) -> None:
        if self.activity is None:
            raise ImproperlyConfigured("activity field must be set before action")

        url_username = self.kwargs.get("username")
        login_user: User = self.request.user
        is_current_user = login_user.username == url_username

        whom: User | None = (
            None if is_current_user else get_object_or_404(User, username=url_username)
        )

        self.action(login_user=login_user, whom=whom, is_current=is_current_user)

        if not is_current_user:
            self.visitor(whom, login_user)

    @staticmethod
    def get_action_message(activity: str, is_owner: bool) -> str:
        return (
            getattr(ActionMessage, f"OWN_{activity}")
            if is_owner
            else getattr(ActionMessage, f"SB_{activity}")
        )
