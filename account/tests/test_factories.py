from django.contrib.auth.models import User
from django.test import TestCase, tag
from faker import Faker

from account.factories import AboutUserFactory, UserFactory, VisitorFactory
from account.models import AboutUser, Profile, Visitor
from action.factories import ActionFactory
from action.models import Action
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


@tag("fv")
class VisitorFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(VisitorFactoryTest, cls).setUpClass()
        VisitorFactory.create_batch(3)

    def test_should_create_six_users(self):
        self.assertEqual(User.objects.count(), 6)

    def test_should_create_three_visitors(self):
        self.assertEqual(Visitor.objects.count(), 3)

    def test_should_create_new_visitors(self):
        from collections import Counter

        users = UserFactory.create_batch(2)
        visitors = VisitorFactory.create_batch(3, visitor=users[0], receiver=users[1])
        self.assertEqual(len(visitors), 3)
        count_visitors = Counter([v.visitor for v in visitors])
        count_receiver = Counter([v.receiver for v in visitors])

        self.assertEqual(count_receiver[users[1]], 3)
        self.assertEqual(count_visitors[users[0]], 3)


@tag("af")
class ActionFactoriesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ActionFactory.create_batch(5)

    def test_should_create_10_users(self):
        self.assertEqual(User.objects.count(), 10)

    def test_should_create_5_actions(self):
        self.assertEqual(Action.objects.count(), 5)

    def test_all_actions_do_not_have_action_field_when_is_default(self):
        self.assertFalse(all([a.action for a in Action.objects.all()]))
