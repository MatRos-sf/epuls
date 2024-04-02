from django.contrib.auth.models import User
from django.test import TestCase, tag
from faker import Faker

from account.factories import AboutUserFactory, ProfileFactory, UserFactory
from account.models import AboutUser, Diary, Profile
from puls.models import Puls

FAKE = Faker()


def generate_username() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=["username"])["username"]


def generate_email() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=["mail"])["mail"]


class TestUserFactory(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestUserFactory, cls).setUpClass()
        UserFactory.create_batch(10)

    def test_should_created_eleven_users(self):
        self.assertEqual(User.objects.count(), 10)

    def test_when_user_is_created_should_trigger_signals(self):
        """
        When user is created, it should create models: AboutUser, Profile and Puls
        """
        amt_of_users = User.objects.count()
        self.assertTrue(
            amt_of_users
            == Profile.objects.count()
            == AboutUser.objects.count()
            == Puls.objects.count()
        )

    def test_should_create_custom_user(self):
        expected_username = generate_username()
        expected_email = generate_email()
        user = UserFactory.create(
            username=expected_username, email=expected_email, password="<PASSWORD>"
        )

        self.assertEqual(User.objects.last(), user)


class ProfileFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileFactoryTest, cls).setUpClass()
        UserFactory.create_batch(2)

    def setUp(self):
        self.profile = Profile.objects.first()

    def test_should_create_two_profile(self):
        self.assertEquals(Profile.objects.count(), 2)

    def test_should_create_two_aboutuser_models(self):
        self.assertEquals(AboutUser.objects.count(), 2)

    def test_should_create_two_pulses_models(self):
        self.assertEquals(Puls.objects.count(), 2)


class AboutUserFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(AboutUserFactoryTest, cls).setUpClass()
        AboutUserFactory.create_batch(3)

    def test_should_create_three_models(self):
        self.assertEquals(AboutUser.objects.count(), 3)
