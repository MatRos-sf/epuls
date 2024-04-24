from django.contrib.auth.models import User
from django.test import TestCase, tag

from shouter.factory import ShouterFactory
from shouter.models import Shouter


@tag("f_s")
class ShouterFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ShouterFactory.create_batch(3)

    def test_should_create_3_users_and_shouters(self):
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Shouter.objects.count(), 3)
