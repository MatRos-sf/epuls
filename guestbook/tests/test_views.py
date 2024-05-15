from functools import partial

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import tag
from notifications.models import Notification

from account.factories import PASSWORD
from account.models import Visitor
from action.models import Action, ActionMessage
from epuls_tools.test import SimpleDBTestCase
from guestbook.factory import GuestbookFactory
from guestbook.models import Guestbook


@tag("v_gb")
class GuestbookViewTestCase(SimpleDBTestCase):
    @classmethod
    def setUpClass(cls):
        super(GuestbookViewTestCase, cls).setUpClass()
        # last 2 users have created entry to main useer

        user1, user2 = User.objects.all()[1:3]
        main_user = User.objects.first()

        # entries
        GuestbookFactory(sender=user1, receiver=main_user)
        GuestbookFactory(sender=user2, receiver=main_user)

    def setUp(self):
        self.url = partial(reverse, "account:guestbook")
        self.user = User.objects.first()
        self.client.login(username=self.user.username, password=PASSWORD)

    def test_when_main_user_visit_yours_gb_should_have_2_entries(self):
        response = self.client.get(self.url(kwargs={"username": self.user.username}))

        object_list = response.context.get("object_list")

        self.assertEqual(object_list.count(), 2)

    def test_when_user_visit_sb_gb_should_not_see_anny_entries(self):
        user = User.objects.last()
        response = self.client.get(self.url(kwargs={"username": user.username}))

        object_list = response.context.get("object_list")

        self.assertEqual(object_list.count(), 0)

    def test_user_cannot_add_entry_on_own_gb(self):
        payload = {"entry": "Hello"}
        response = self.client.post(
            self.url(kwargs={"username": self.user.username}), data=payload
        )

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], "You have created a entry for this guestbook.")

    def test_user_can_add_entry_when_entry_was_not_added(self):
        payload = {"entry": "Hello"}
        user = User.objects.last()
        response = self.client.post(
            self.url(kwargs={"username": user.username}),
            data=payload,
        )

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], "An entry has been added!")

        self.assertEqual(Guestbook.objects.filter(sender=self.user).count(), 1)

    def test_should_not_add_entry_when_user_has_added_the_one(self):
        payload = {"entry": "Hello"}
        user = User.objects.last()
        self.client.post(self.url(kwargs={"username": user.username}), data=payload)
        self.assertEqual(Guestbook.objects.filter(sender=self.user).count(), 1)

        response = self.client.post(
            self.url(kwargs={"username": user.username}), data=payload
        )

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], "You have created a entry for this guestbook.")
        self.assertEqual(Guestbook.objects.filter(sender=self.user).count(), 1)

    def test_should_create_action_and_visitor_when_user_post_entry(self):
        payload = {"entry": "Hello"}
        user = User.objects.last()
        self.client.post(self.url(kwargs={"username": user.username}), data=payload)

        action = Action.objects.first()
        self.assertEqual(action.action, ActionMessage.SB_GUESTBOOK)

        visitor = Visitor.objects.first()
        self.assertEqual(visitor.visitor, self.user)
        self.assertEqual(visitor.receiver, user)

    def test_should_create_notification(self):
        payload = {"entry": "Hello"}
        user = User.objects.last()
        self.client.post(
            self.url(kwargs={"username": user.username}),
            data=payload,
        )

        self.assertEqual(Notification.objects.count(), 1)
