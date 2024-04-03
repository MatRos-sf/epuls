from functools import partial
from http import HTTPStatus

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase, tag
from parameterized import parameterized

from account.factories import PASSWORD, UserFactory
from account.models import ProfileType


class SimpleDBTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SimpleDBTestCase, cls).setUpClass()
        users = UserFactory.create_batch(6)
        main_user = users[0]

        for user in users[1:]:
            main_user.profile.friends.add(user)


@tag("bf")
class BestFriendsListViewTestCase(SimpleDBTestCase):
    def setUp(self):
        self.user = User.objects.first()
        self.url = reverse("account:best-friends")

    def test_should_create_one_user_who_has_5_friends(self):
        self.assertEqual(self.user.profile.friends.count(), 5)

    def test_user_can_see_view_when_profile_is_basic(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    @parameterized.expand([ProfileType.DIVINE, ProfileType.PRO, ProfileType.XTREME])
    def test_should_visit_endpoint_when_user_does_not_have_basic_profile_type(
        self, profile_type
    ):
        self.user.profile.type_of_profile = profile_type
        self.user.profile.save()

        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_should_not_have_any_bf_in_context(self):
        self.user.profile.type_of_profile = ProfileType.DIVINE
        self.user.profile.save()

        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # chceck context
        context = response.context["bf_list"]
        self.assertFalse(context)

    def test_should_have_bf_in_context(self):
        # change profile type
        self.user.profile.type_of_profile = ProfileType.DIVINE

        # add bf
        users = User.objects.all()[1:3]
        self.user.profile.best_friends.add(*users)

        self.user.profile.save()
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # chceck context
        context = response.context["bf_list"]
        self.assertEqual(len(context), 2)


@tag("bf_add")
class AddBestFriendsViewTestCase(SimpleDBTestCase):
    @classmethod
    def setUpClass(cls):
        super(AddBestFriendsViewTestCase, cls).setUpClass()

        # main user has ProfileType.DIVINE and 3 bfs
        main_user = User.objects.first()
        main_user.profile.type_of_profile = ProfileType.DIVINE

        bfs = User.objects.all()[1:4]
        main_user.profile.best_friends.add(*bfs)
        main_user.profile.save()

    def setUp(self):
        self.user = User.objects.first()
        self.url = partial(reverse, "account:best-friend-add")

    def test_should_add_new_bf(self):
        new_bf = User.objects.last()

        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(self.url(kwargs={"pk": new_bf.pk}))

        self.assertEqual(self.user.profile.best_friends.count(), 4)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(
            messages[0], f"{new_bf.username} has been added to your best friends list."
        )

    def test_should_not_add_new_bf_when_new_user_is_not_in_friends_list(self):
        new_user = UserFactory()

        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(self.url(kwargs={"pk": new_user.pk}))

        self.assertEqual(self.user.profile.best_friends.count(), 3)

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(
            messages[0],
            "You cannot add best friend if friend is not in your friends list or you are the best friend",
        )

    def test_should_not_add_bf_when_user_has_basic_account(self):
        self.user.profile.change_type_of_profile(ProfileType.BASIC)
        self.user.profile.save()

        self.assertEqual(self.user.profile.best_friends.count(), 0)

        new_bf = User.objects.last()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(self.url(kwargs={"pk": new_bf.pk}))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(self.user.profile.best_friends.count(), 0)

    def test_should_return_404_when_user_does_not_exist(self):
        from random import randint

        self.client.login(username=self.user.username, password=PASSWORD)
        rseponse = self.client.post(self.url(kwargs={"pk": randint(15, 100)}))
        self.assertEqual(rseponse.status_code, 404)
