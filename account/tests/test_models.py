from django.test import TestCase

from account.factories import UserFactory
from account.models import AboutUser, Profile


class ProfileModelTest(TestCase):
    def test_should_create_profile_and_about_user_when_user_is_created(self):
        UserFactory.create(username="test", password="<PASSWORD>")

        self.assertEquals(Profile.objects.count(), 1)
        self.assertEquals(AboutUser.objects.count(), 1)

    def test_should_create_ten_users_profile_and_about_me(self):
        UserFactory.create_batch(10)

        self.assertEquals(Profile.objects.count(), 10)
        self.assertEquals(AboutUser.objects.count(), 10)
