"""
Here are custom mixins for views
"""
from django.contrib.auth.mixins import UserPassesTestMixin

from account.models import ProfileType


class UsernameMatchesMixin(UserPassesTestMixin):
    """
    A mixin that checks if the current user matches the username specified in the endpoint kwargs.
    """

    def test_func(self) -> bool:
        return self.kwargs.get("username") == self.request.user.username


class NotBasicTypeMixin(UserPassesTestMixin):
    """
    Checks if the current user doesn't have a basic account'
    """

    def test_func(self) -> bool:
        return self.request.user.profile.type_of_profile != ProfileType.BASIC
