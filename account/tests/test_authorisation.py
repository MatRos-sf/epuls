from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase, tag
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode

from account.factories import UserFactory
from epuls_tools.scaler import CONSTANT_PULS_QTY
from puls.models import PulsType, SinglePuls


@tag("a_tc")
class ActivateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ActivateTestCase, cls).setUpClass()
        UserFactory()

    def setUp(self):
        self.user = User.objects.first()

        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_should_activate_account_when_provide_correct_url(self):
        self.client.get(
            reverse(
                "account:activate", kwargs={"uidb64": self.uid, "token": self.token}
            )
        )

        self.assertTrue(self.user.profile.is_confirm)

    def test_should_show_positive_message_when_email_is_confirm(self):
        expected_message = "Your account has been confirmed!"
        response = self.client.get(
            reverse(
                "account:activate", kwargs={"uidb64": self.uid, "token": self.token}
            )
        )
        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], expected_message)

    def test_should_create_single_puls_when_user_confirm_email(self):
        self.client.get(
            reverse(
                "account:activate", kwargs={"uidb64": self.uid, "token": self.token}
            )
        )

        self.assertEqual(SinglePuls.objects.count(), 1)
        puls = SinglePuls.objects.first()

        self.assertEqual(puls.type, PulsType.ACCOUNT_CONFIRM)
        self.assertEqual(puls.quantity, CONSTANT_PULS_QTY)

    def test_should_create_new_token(self):
        expected_message = (
            "Token has expired. New confirmation link has been sent to your email."
        )

        with patch(
            "django.contrib.auth.tokens.default_token_generator.check_token"
        ) as mock_check_token:
            mock_check_token.return_value = False

            response = self.client.get(
                reverse(
                    "account:activate", kwargs={"uidb64": self.uid, "token": self.token}
                )
            )

            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual(messages[0], expected_message)

    def test_should_show_warning_when_user_try_confirm_account_who_it_has_been_confirmed(
        self,
    ):
        expected_message = "Your email was confirmed!"
        self.user.profile.is_confirm = True
        self.user.profile.save()

        response = self.client.get(
            reverse(
                "account:activate", kwargs={"uidb64": self.uid, "token": self.token}
            )
        )

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], expected_message)
