"""
Here are custom mixins for views
"""
from django.contrib.auth.mixins import UserPassesTestMixin


class UsernameMatchesMixin(UserPassesTestMixin):
    """
    A mixin that checks if the current user matches the username specified in the endpoint kwargs.
    """

    def test_func(self):
        return self.kwargs.get("username") == self.request.user
