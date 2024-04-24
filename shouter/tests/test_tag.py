from django.test import TestCase, tag

from account.factories import UserFactory
from shouter.templatetags.shouter_tag import make_user_tag


@tag("mut_t")
class MakeUserTagFunctionTestCase(TestCase):
    def test_should_render_correct_tag(self):
        user = UserFactory()
        expected = f'<a href="/{user.username}/">{user.username}</a>'
        response = make_user_tag(user)

        self.assertEqual(expected, response)
