from http import HTTPStatus

from django.shortcuts import reverse
from django.test import TestCase, tag
from parameterized import parameterized

from account.factories import PASSWORD, UserFactory
from account.models import Diary

APP_NAME = "account:"


@tag("profile")
class ProfileViewTests(TestCase):
    def setUp(self):
        self.url_name = "account:profile"

    def test_should_enter_to_profile_view_by_url_name(self):
        user = UserFactory(username="test")
        self.client.login(username=user.username, password="1_test_TEST_!")
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": user.username})
        )

        self.assertEqual(response.status_code, 200)


@tag("update_profile")
class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.url_name = APP_NAME + "profile-update"
        self.userOne = UserFactory(username="test_1")
        self.userTwo = UserFactory(username="test_2")

    def test_should_enter_to_profile_update_view_by_url_name(self):
        self.client.login(username=self.userOne.username, password=PASSWORD)

        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.userOne.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_not_enter_to_profile_update_view_when_profile_is_not_property(self):
        self.client.login(username=self.userOne.username, password=PASSWORD)

        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.userTwo.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FORBIDDEN)

    def test_should_be_message_when_user_doesnt_have_permission_to_update_profile(self):
        expected = {"message": "You do not have permission to update this user."}
        self.client.login(username=self.userOne.username, password=PASSWORD)

        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.userTwo.username})
        )
        message = response.content

        self.assertJSONEqual(str(message, encoding="utf-8"), expected)


# Library
@tag("d_c")
class DiaryCreateViewTestCase(TestCase):
    def setUp(self):
        self.url_name = "account:diary-create"
        self.user = UserFactory(username="test")

    def test_endpoint_returns_302_status_code(self):
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.user.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_endpoint_returns_200_status_code(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.user.username})
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_endpoint_returns_403_status_code(self):
        new_user = UserFactory(username="new_user")
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": new_user.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FORBIDDEN)

    def test_template_should_return_appropriate_template(self):
        expected_template = "account/diary/create.html"
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.user})
        )

        self.assertTemplateUsed(response, expected_template)

    def test_should_create_object_when_payload_is_correct(self):
        payload = {"title": "test_diary", "content": "test_content"}
        self.client.login(username=self.user.username, password=PASSWORD)
        self.client.post(
            reverse(self.url_name, kwargs={"username": self.user}), data=payload
        )

        self.assertEquals(Diary.objects.count(), 1)

        # author should be currently user
        diary = Diary.objects.first()
        self.assertEquals(diary.author, self.user)

    def test_should_redirect_when_object_is_create(self):
        payload = {
            "author": self.user,
            "title": "test_diary",
            "content": "test_content",
        }
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(
            reverse(self.url_name, kwargs={"username": self.user}), data=payload
        )

        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    @parameterized.expand(
        [({"title": "test_diary"},), ({"content": "test_content"},), ({},)]
    )
    def test_should_not_create_object_when_payload_is_incorrect(self, payload):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(
            reverse(self.url_name, kwargs={"username": self.user}), data=payload
        )
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Diary.objects.count(), 0)

    def test_should_not_create_object_when_user_is_not_owner(self):
        new_user = UserFactory(username="new_user")
        payload = {
            "author": self.user,
            "title": "test_diary",
            "content": "test_content",
        }
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(
            reverse(self.url_name, kwargs={"username": new_user.username}), data=payload
        )

        self.assertEquals(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(Diary.objects.count())


@tag("d_r")
class DiaryDetailViewTestCase(TestCase):
    def setUp(self):
        self.url_name = "account:diary-detail"
        self.user = UserFactory(username="test")

    def test_endpoint_returns_302_status_code(self):
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.user.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_endpoint_returns_200_status_code(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": self.user.username})
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_endpoint_returns_403_status_code(self):
        new_user = UserFactory(username="new_user")
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(
            reverse(self.url_name, kwargs={"username": new_user.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FORBIDDEN)
