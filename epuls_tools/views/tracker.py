from enum import StrEnum, auto
from functools import wraps
from typing import Any, Optional

from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from account.models import Profile, Visitor
from action.models import Action, ActionMessage
from epuls_tools.expections import TrackerUserNotFoundError


class ActionType(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    PROFILE = auto()
    GUESTBOOK = auto()
    DIARY = auto()
    FRIENDS = auto()
    GALLERY = auto()
    PHOTO = auto()
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
    """This class should be only using with django Views"""

    activity = None

    def get_login_user(self) -> User:
        """
        Returns the currently logged-in user.
        If the `current_user` attribute already exists in the object, it returns its value.
        Otherwise, it sets `current_user` to the user from `self.request.user` and returns it.
        """
        try:
            login_user = getattr(self, "current_user")
        except AttributeError:
            setattr(self, "current_user", self.request.user)
            login_user = self.current_user

        return login_user

    def get_user(self) -> User:
        """
        Retrieves the user associated with the instance. If the user object is already stored, it retrieves and returns it.
        Otherwise, it tries to capture the user.
        """
        user = getattr(self, "user_object", None)
        if not user:
            user = self.capture_user()
            setattr(self, "user_object", user)

        return user

    def capture_user(self) -> User:
        """
        Tries to capture user instance.
        You can customize the way user is captured by defining your own capture method starting with 'capture_user_'
        and implementing them in this class or its subclasses.
        """
        capture_method = [
            method for method in dir(self) if method.startswith("capture_user_")
        ]

        for method in capture_method:
            user = getattr(self, method)()
            if user:
                return user

        # user not found
        raise TrackerUserNotFoundError()

    def capture_user_from_url(self) -> Optional[User]:
        """Tries to capture user from the URL parameter 'username'"""
        try:
            url_username = self.kwargs.get("username", None)
        except AttributeError:
            return

        return get_object_or_404(User, username=url_username) if url_username else None

    def capture_user_from_instance(self) -> Optional[User]:
        """
        Tries to capture user from the instance.

        The instance may contain the user information stored in different fields such as 'user' or 'profile'.
        If the instance has a profile, the user is expected to be found within the profile.

        """
        # query set isn't support
        try:
            instance = self.object
        except AttributeError:
            return

        user = getattr(instance, "user", None) or getattr(instance, "profile", None)

        if isinstance(user, Profile):
            user = user.user

        return user

    def check_users(self) -> bool:
        """
        Checks if the currently logged-in user (from 'login_user') is the same  as the user associated with the URL parameter 'username' (from 'url_user').
        """
        return self.get_user() == self.get_login_user()

    @validate_view_inheritance
    def tracker(self) -> None:
        if self.activity is None:
            raise ImproperlyConfigured("activity field must be set before action")

        whom = self.get_user()
        login_user: User = self.get_login_user()
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
