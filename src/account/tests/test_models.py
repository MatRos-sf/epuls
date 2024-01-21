from django.test import TestCase

from django.contrib.auth.models import User
from account.models import Profile

class ProfileModelTest(TestCase):

    def test_should_create_profile_when_user_is_created(self):
        User.objects.create_user(username='test', password='<PASSWORD>')

        self.assertEquals(Profile.objects.count(), 1)

