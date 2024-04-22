from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from account.factories import PASSWORD, UserFactory
from shouter.templatetags.shouter_tag import make_user_tag, shouter


@tag("mut_t")
class MakeUserTagFunctionTestCase(TestCase):
    def test_should_render_correct_tag(self):
        user = UserFactory()
        expected = f'<a href="/{user.username}/">{user.username}</a>'
        response = make_user_tag(user)

        self.assertEqual(expected, response)
