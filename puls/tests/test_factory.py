from datetime import timedelta

from django.test import TestCase, tag
from django.utils import timezone

from account.factories import UserFactory
from puls.factories import PulsFactory, SinglePulsFactory
from puls.models import Puls, SinglePuls


@tag("sss")
class PulsFactoryTestCase(TestCase):
    def test_should_create_5_puls_model(self):
        UserFactory.create_batch(5)
        self.assertEqual(Puls.objects.count(), 5)


class SinglePulsFactoryTestCase(TestCase):
    def test_should_create_model(self):
        SinglePulsFactory()
        self.assertEqual(SinglePuls.objects.count(), 1)

    def test_shoud_be_random_quantity(self):
        puls = SinglePulsFactory()

        self.assertGreater(puls.quantity, 1)
        self.assertLess(puls.quantity, 10)
