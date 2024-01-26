from django.test import TestCase, tag
from django.shortcuts import reverse

from account.factories import UserFactory

@tag('profile')
class ProfileViewTests(TestCase):
    def setUp(self):
        self.url_name = 'account:profile'

    def test_should_enter_to_profile_view_by_url_name(self):
        user = UserFactory(username='test')
        s = self.client.login(username=user.username, password='1_test_TEST_!')
        response = self.client.get(reverse(self.url_name, kwargs={'username': user.username}))

        self.assertEqual(response.status_code, 200)
