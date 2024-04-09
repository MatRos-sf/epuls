from django.contrib.auth.models import User
from django.test import TestCase, tag

from guestbook.factory import GuestbookFactory


@tag("f_gb")
class GuestbookFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        GuestbookFactory.create_batch(3)

    def test_should_create_six_users(self):
        self.assertEqual(User.objects.count(), 6)

    def test_when_factory_is_created_should_set_random_entry(self):
        entry = GuestbookFactory()
        self.assertIsInstance(entry.entry, str)
