import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase, tag
from django.utils import timezone
from parameterized import parameterized

from account.factories import PASSWORD, UserFactory
from shouter.factory import ShouterFactory
from shouter.models import Shouter


@tag("scv_t")
class ShouterCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        UserFactory()

    def setUp(self):
        self.user = User.objects.first()
        self.client.login(username=self.user.username, password=PASSWORD)
        self.url = reverse("shouter:create")
        self.payload = {"shouter": "test-shouter", "time": 1}

    def test_should_valid_form_when_payload_is_correct(self):
        response = self.client.post(self.url, data=self.payload)

        self.assertRedirects(response, self.url)
        self.assertEqual(Shouter.objects.count(), 1)

    @parameterized.expand([(1,), (5,), (24,)])
    def test_should_set_property_expiration_datetime(self, payload_time):
        self.payload["time"] = payload_time

        with patch("shouter.views.timezone.now") as mock_time:
            fake_date = datetime.datetime(2017, 2, 1, tzinfo=datetime.timezone.utc)

            mock_time.return_value = fake_date
            self.client.post(self.url, data=self.payload)

            shouter = Shouter.objects.first()

            self.assertEqual(shouter.created, fake_date)
            self.assertEqual(
                shouter.expiration, fake_date + datetime.timedelta(hours=payload_time)
            )

    @parameterized.expand(
        [
            ({},),
            ({"time": 1},),
            ({"shouter": "test"},),
            ({"shouter": "test", "time": 5116},),
        ]
    )
    def test_shouter_is_not_created_when_form_is_invalid(self, payload):
        self.client.post(self.url, data=payload)

        self.assertFalse(Shouter.objects.count())
