from enum import StrEnum, auto
from functools import wraps
from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from account.models import Profile, Visitor
from action.models import Action, ActionMessage


class ActionType(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    PROFILE = auto()
    GUESTBOOK = auto()
    DIARY = auto()
    FRIENDS = auto()
    GALLERY = auto()
    PULS = auto()


def validate_view_inheritance(method):
    """
    Decorator that checks if a method is a subclass of the Django View class.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not issubclass(self.__class__, View):
            raise ImproperlyConfigured(
                f"Class {self.__class__.__name__} must be subclass of django.views.View"
            )
        return method(self, *args, **kwargs)

    return wrapper


def add_visitor(whom: User, login_user: User) -> None:
    """
    Updates the visitor count for a gender-specific field in the Profile model.

    Parameters:
        - whom (User): The user whose profile is being visited.
        - login_user (User): The user who is visiting the profile.
    """
    user_gender = login_user.profile.get_gender_display().lower()

    try:
        whom.profile.visitors.add(login_user)

        Profile.objects.filter(pk=whom.pk).update(
            **{f"{user_gender}_visitor": F(f"{user_gender}_visitor") + 1}
        )

    except FieldDoesNotExist as e:
        raise e


def create_visitor(whom: User, login_user: User) -> None:
    """
    Creates a visitor who visits the profile of someone and triggers the add_visitor function
    Parameters:
        - whom (User): The user whose profile is being visited.
        - login_user (User): The user who is visiting the profile.
    """
    Visitor.objects.create(visitor=login_user, receiver=whom)

    # add only first time
    if not whom.profile.visitors.filter(pk=login_user.pk).exists():
        # add gender to the counter
        add_visitor(whom, login_user)


def create_action(
    *, login_user: User, whom: User, is_current: bool, activity: ActionType
) -> None:
    """
    Track user activity and create or update Action models.
    If the last recorded Action from the user is the same as the current activity, only update the date field
    of the last action. Unless the last Action is different or there's no previous action then create new one.
    """
    # capture action message
    action_message = EpulsTracker.get_action_message(activity, is_current)

    last_action = Action.last_user_action(who=login_user)

    # update Action when Action exists and is the same that last one or create new
    if last_action and last_action.action == action_message:
        last_action.date = timezone.now()
        last_action.save(update_fields=["date"])
    else:
        Action.objects.create(who=login_user, whom=whom, action=action_message)


class EpulsTracker:
    activity = None

    def login_user(self) -> User:
        """
        Returns the currently logged-in user. If the `current_user` attribute already exists in the object, it returns its value. Otherwise, it sets
        `current_user` to the user from `self.request.user` and returns it.
        """
        try:
            login_user = getattr(self, "current_user")
        except AttributeError:
            setattr(self, "current_user", self.request.user)
            login_user = self.current_user

        return login_user

    def url_user(self) -> User:
        """
        Returns the user associated with the URL parameter 'username'.
        If the user object is already stored in the instance attribute, it retrieves and returns it.
        Otherwise, it fetches the user from the URL parameter and stores it in the attribute before returning it.
        """
        try:
            user = getattr(self, "url_user_object")
        except AttributeError:
            url_username = self.kwargs.get("username")
            user = get_object_or_404(User, username=url_username)
            setattr(self, "url_user_object", user)

        return user

    def check_users(self) -> bool:
        """
        Checks if the currently logged-in user (from 'login_user') is the same  as the user associated with the URL parameter 'username' (from 'url_user').
        """
        return self.url_user() == self.login_user()

    @validate_view_inheritance
    def tracker(self) -> None:
        if self.activity is None:
            raise ImproperlyConfigured("activity field must be set before action")

        whom = self.url_user()
        login_user: User = self.login_user()
        is_current_user = self.check_users()

        create_action(
            login_user=login_user,
            whom=whom,
            is_current=is_current_user,
            activity=self.activity,
        )

        if not is_current_user:
            create_visitor(whom, login_user)

    @staticmethod
    def get_action_message(activity: str, is_owner: bool) -> str:
        return (
            getattr(ActionMessage, f"OWN_{activity}")
            if is_owner
            else getattr(ActionMessage, f"SB_{activity}")
        )

    def get(self, request, *args, **kwargs) -> Any:
        """
        Overwrite method and add tracker system.
        """
        response = super().get(request, *args, **kwargs)
        self.tracker()
        return response
