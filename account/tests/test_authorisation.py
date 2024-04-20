from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.db.models import Sum
from django.shortcuts import reverse
from django.test import TestCase, tag
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
from parameterized import parameterized

from account.factories import PASSWORD, UserFactory
from account.models import ProfileType
from epuls_tools.scaler import (
    CONSTANT_PULS_QTY,
    EXTRA_PULS_BY_PROFILE_TYPE,
    PULS_FOR_ACTION,
)
from puls.models import PulsType, SinglePuls


class DataSetWithOneUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        UserFactory()


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


@tag("el_tc")
class EpulsLoginViewTestCase(DataSetWithOneUser):
    def setUp(self):
        self.user = User.objects.first()
        self.url = reverse("account:login")

        self.credentials = {"username": self.user.username, "password": PASSWORD}

    def test_should_login_user_when_credentials_is_correct(self):
        response = self.client.post(self.url, data=self.credentials)

        self.assertRedirects(response, reverse("account:home"))

    def test_should_give_away_puls_when_user_login(self):
        self.client.post(self.url, data=self.credentials)

        puls = SinglePuls.objects.first()

        self.assertEqual(puls.quantity, 0.05)

    def test_should_give_away_pulses_when_user_login_and_logout_few_times(self):
        expected = 0.05 * 10

        for _ in range(10):
            self.client.get(self.url, data=self.credentials)
            self.client.post(self.url, data=self.credentials)

        quantity = SinglePuls.objects.filter(puls__profile__user=self.user).aggregate(
            Sum("quantity")
        )["quantity__sum"]

        self.assertAlmostEqual(quantity, expected)

    def test_should_logout_user_when_user_try_login_when_is_login(self):
        expected_message = "You have been logout!"

        self.client.login(
            username=self.credentials["username"], password=self.credentials["password"]
        )

        response = self.client.get(self.url)

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], expected_message)

    @parameterized.expand([ProfileType.PRO, ProfileType.XTREME, ProfileType.DIVINE])
    def test_should_give_extra_puls_for_login_when_user_does_not_have_basic_account(
        self, top
    ):
        self.user.profile.type_of_profile = top
        self.user.profile.save()
        expected = PULS_FOR_ACTION[PulsType.LOGINS] * EXTRA_PULS_BY_PROFILE_TYPE[top]

        self.client.post(self.url, data=self.credentials)
        puls = SinglePuls.objects.first()

        self.assertAlmostEqual(puls.quantity, expected)
        self.assertGreater(puls.quantity, PULS_FOR_ACTION.get(PulsType.LOGINS))
