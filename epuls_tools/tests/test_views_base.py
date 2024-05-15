from django.test import TestCase
from notifications.models import Notification

from account.factories import UserFactory
from epuls_tools.views.base import EpulsBaseView


class EpulsBaseViewTestCase(TestCase):
    def test_should_create_notification(self):
        user_one, user_two = UserFactory.create_batch(2)
        bv = EpulsBaseView()
        bv.current_user = user_one
        bv.user_object = user_two

        bv.send_notification("test")

        self.assertEqual(Notification.objects.count(), 1)

    def test_should_raise_some_exception_when_there_are_not_set_atributes(self):
        bv = EpulsBaseView()

        with self.assertRaises(Exception):
            bv.send_notification("test")
