import os
from datetime import timedelta
from functools import partial
from http import HTTPStatus
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.base import File
from django.shortcuts import reverse
from django.test import tag
from django.utils import timezone
from parameterized import parameterized
from PIL import Image

from account.factories import PASSWORD, UserFactory, VisitorFactory
from account.models import Profile, ProfileType, Visitor
from action.factories import ActionFactory
from action.models import Action, ActionMessage

from .test_data import SimpleDBTestCase


@tag("vp")
class ProfileViewTestCase(SimpleDBTestCase):
    def setUp(self):
        self.url = partial(reverse, "account:profile")
        self.user = User.objects.first()
        self.client.login(username=self.user.username, password=PASSWORD)

        self.temp_image_file = []

    def tearDown(self):
        super().tearDown()
        if self.temp_image_file:
            for image_path in self.temp_image_file:
                if os.path.exists(image_path):
                    os.remove(image_path)

    def test_context_should_have_extra_values(self):
        sample_user = User.objects.last()
        response = self.client.get(self.url(kwargs={"username": sample_user.username}))

        self.assertEqual(response.status_code, HTTPStatus.OK)

        context = response.context

        self.assertIsNone(context["action"])
        self.assertIsNone(context["visitors"])
        self.assertFalse(context["self"])

    def test_should_return_context_self_true_when_user_is_on_own_website(self):
        response = self.client.get(self.url(kwargs={"username": self.user.username}))

        context_self = response.context["self"]
        self.assertTrue(context_self)

    def __change_profile_type(self, profile_type: str) -> None:
        self.user.profile.type_of_profile = profile_type
        self.user.profile.save()

    @parameterized.expand(
        [ProfileType.DIVINE, ProfileType.PRO, ProfileType.XTREME, ProfileType.BASIC]
    )
    def test_should_display_correct_number_of_visitors(self, profile_type):
        # set new profile
        self.__change_profile_type(profile_type)

        # user who profile will be visited
        receiver = User.objects.last()

        # 3 different Users
        user_1, user_2, user_3 = User.objects.all()[1:4]

        # creat 3 different visitors
        VisitorFactory(visitor=user_1, receiver=receiver)
        VisitorFactory(visitor=user_2, receiver=receiver)
        VisitorFactory(visitor=user_3, receiver=receiver)

        # Patch dictionary to set specific visitor count for profile type
        with patch.dict(
            "account.models.TYPE_OF_PROFILE", {profile_type: {"sb_visitors": 2}}
        ):
            response = self.client.get(self.url(kwargs={"username": receiver.username}))

            context_visitor = response.context["visitors"]
            self.assertEqual(len(context_visitor), 2)

    @parameterized.expand(
        [ProfileType.DIVINE, ProfileType.PRO, ProfileType.XTREME, ProfileType.BASIC]
    )
    def test_should_display_correct_number_of_visitors_when_user_is_on_own_profile(
        self, profile_type
    ):
        # set new profile
        self.__change_profile_type(profile_type)

        # 3 different Users
        user_1, user_2, user_3 = User.objects.all()[1:4]

        # creat 3 different visitors
        VisitorFactory(visitor=user_1, receiver=self.user)
        VisitorFactory(visitor=user_2, receiver=self.user)
        VisitorFactory(visitor=user_3, receiver=self.user)

        # Patch dictionary to set specific visitor count for profile type
        with patch.dict(
            "account.models.TYPE_OF_PROFILE", {profile_type: {"own_visitors": 2}}
        ):
            response = self.client.get(
                self.url(kwargs={"username": self.user.username})
            )

            context_visitor = response.context["visitors"]
            self.assertEqual(len(context_visitor), 2)

    @parameterized.expand(
        [ProfileType.DIVINE, ProfileType.PRO, ProfileType.XTREME, ProfileType.BASIC]
    )
    def test_should_display_only_one_visitor_when_all_visitors_are_duplicated(
        self, profile_type
    ):
        # set new profile
        self.__change_profile_type(profile_type)

        # user who profile will be visited
        receiver = User.objects.last()

        # creat 3 different visitors
        VisitorFactory.create_batch(5, visitor=self.user, receiver=receiver)

        # Patch dictionary to set specific visitor count for profile type
        with patch.dict(
            "account.models.TYPE_OF_PROFILE", {profile_type: {"sb_visitors": 2}}
        ):
            response = self.client.get(self.url(kwargs={"username": receiver.username}))

            context_visitor = response.context["visitors"]
            self.assertEqual(len(context_visitor), 1)

    def generate_photo_file(self, name="test"):
        name = name if name.endswith(".jpg") else name + ".jpg"
        file_obj = BytesIO()
        color = (256, 0, 0)
        image = Image.new("RGB", size=(200, 200), color=color)
        image.save(file_obj, format="JPEG")

        file_obj.seek(0)

        return File(file_obj, name=name)

    def test_delete_photo_owned_by_another_user_should_not_work(self):
        # add new profile photo
        self.user.profile.profile_picture = self.generate_photo_file(name="test")
        self.user.profile.save()

        # add new photo to list because it is delete when test is finish
        self.temp_image_file.append(self.user.profile.profile_picture.path)

        self.assertTrue(Profile.objects.get(user=self.user).profile_picture)
        # logout current user
        self.client.logout()
        # login different user
        user = User.objects.last()
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.post(self.url(kwargs={"username": self.user.username}))

        # profile picture hasn't been deleted!
        self.assertTrue(Profile.objects.get(user=self.user).profile_picture)

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(
            messages[0],
            "You can't delete profile picture because you are not the owner of this profile.",
        )

    def test_delete_user_photo_should_work_when_user_is_owner(self):
        # add new profile photo
        self.user.profile.profile_picture = self.generate_photo_file(name="test")
        self.user.profile.save()

        # add new photo to list because it is delete when test is finish
        self.temp_image_file.append(self.user.profile.profile_picture.path)

        self.assertTrue(Profile.objects.get(user=self.user).profile_picture)

        response = self.client.post(self.url(kwargs={"username": self.user.username}))

        # profile picture has been deleted!
        self.assertFalse(Profile.objects.get(user=self.user).profile_picture)

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(messages[0], "Profile picture has been deleted.")

    def test_when_user_visit_another_user_profile_should_trigger_tracker_and_create_action_when_is_first_time(
        self,
    ):
        self.assertEqual(Action.objects.count(), 0)

        user = User.objects.last()

        self.client.post(self.url(kwargs={"username": user.username}))

        self.assertEqual(Action.objects.count(), 1)

        action = Action.objects.first()
        self.assertEqual(action.action, ActionMessage.SB_PROFILE)

    def test_when_user_visit_your_profile_should_trigger_tracker_and_create_action_when_is_first_time(
        self,
    ):
        self.assertEqual(Action.objects.count(), 0)

        self.client.post(self.url(kwargs={"username": self.user.username}))

        self.assertEqual(Action.objects.count(), 1)

        action = Action.objects.first()
        self.assertEqual(action.action, ActionMessage.OWN_PROFILE)

    def test_when_user_visit_another_user_profile_should_trigger_tracker_and_create_action_when_last_action_was_different(
        self,
    ):
        default_user = User.objects.all()[2]
        ActionFactory(who=self.user, whom=default_user)

        user = User.objects.last()

        self.client.post(self.url(kwargs={"username": user.username}))

        self.assertEqual(Action.objects.count(), 2)

        action = Action.objects.first()
        self.assertEqual(action.action, ActionMessage.SB_PROFILE)

    def test_when_user_visit_another_user_profile_should_trigger_tracker_and_update_action_when_last_action_was_the_same(
        self,
    ):
        user = User.objects.last()

        ActionFactory(
            who=self.user,
            whom=user,
            action=ActionMessage.SB_PROFILE,
            date=timezone.now() - timedelta(days=4),
        )

        self.client.post(self.url(kwargs={"username": user.username}))

        self.assertEqual(Action.objects.count(), 1)

        action = Action.objects.first()
        self.assertEqual(action.action, ActionMessage.SB_PROFILE)
        self.assertEqual(action.date.day, timezone.now().day)

    def test_should_not_create_visitor_when_user_is_on_own_profile(self):
        self.client.post(self.url(kwargs={"username": self.user.username}))

        self.assertFalse(Visitor.objects.count())

    def test_should_create_visitor_when_user_is_not_on_own_profile(self):
        user = User.objects.last()
        self.client.post(self.url(kwargs={"username": user.username}))

        self.assertEqual(Visitor.objects.count(), 1)

    def test_should_create_visitor_and_updated_appropriate_field_when_user_is_not_on_own_profile(
        self,
    ):
        user = User.objects.last()

        self.assertEqual(user.profile.male_visitor, 0)
        self.client.post(self.url(kwargs={"username": user.username}))

        self.assertEqual(Visitor.objects.count(), 1)

        user.refresh_from_db()
        self.assertEqual(user.profile.male_visitor, 1)
