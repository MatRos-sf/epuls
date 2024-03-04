from django.contrib.auth.models import User
from django.test import TestCase, tag

from account.factories import (
    DiaryFactory,
    UserFactory,
    generate_email,
    generate_username,
)
from account.models import Diary


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
            username=expected_username, email=expected_email, password="<PASSWORD>"
        )

        self.assertEqual(User.objects.last(), user)


class TestGenerateUsername(TestCase):
    def test_should_generate_username(self):
        username = generate_username()
        self.assertIsInstance(username, str)


@tag("d_t")
class DiaryFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(DiaryFactoryTest, cls).setUpClass()
        user_one = UserFactory.create(username="user_one")
        user_two = UserFactory.create(username="user_two")

        for _ in range(5):
            DiaryFactory(author=user_one)
            DiaryFactory(author=user_two)

    def test_should_created_10_diaries(self):
        self.assertEqual(Diary.objects.count(), 10)

    def test_user_one_should_have_five_diaries(self):
        self.assertEqual(Diary.objects.filter(author__username="user_one").count(), 5)

    def test_user_two_should_have_five_diaries(self):
        self.assertEqual(Diary.objects.filter(author__username="user_two").count(), 5)
