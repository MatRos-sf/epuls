from django.contrib.auth.models import User
from django.test import TestCase, tag

from diary.factory import DiaryFactory
from diary.models import Diary


@tag("f_d")
class DiaryFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        DiaryFactory.create_batch(3)

    def test_should_create_three_different_users(self):
        self.assertEqual(User.objects.count(), 3)

    def test_should_create_3_diary_models(self):
        self.assertEqual(Diary.objects.count(), 3)

    def test_should_create_random_title_and_content_when_is_created_factory(self):
        diart = Diary()

        self.assertIsInstance(diart.title, str)
        self.assertIsInstance(diart.content, str)
