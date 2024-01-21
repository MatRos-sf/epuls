from django.contrib.auth.models import User
from django.test import TestCase

from account.factories import generate_username, generate_email, UserFactory


class TestUserFactory(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestUserFactory, cls).setUpClass()
        UserFactory.create_batch(10)

    def test_should_created_eleven_users(self):
        self.assertEqual(User.objects.count(), 10)

    def test_should_create_custom_user(self):
        expected_username = generate_username()
        expected_email = generate_email()
        user = UserFactory.create(
            username= expected_username,
            email = expected_email,
            password = '<PASSWORD>'
        )

        self.assertEqual(User.objects.last(), user)


class TestGenerateUsername(TestCase):
    def test_should_generate_username(self):
        username = generate_username()
        self.assertIsInstance(username, str)
