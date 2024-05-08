from functools import partial
from http import HTTPStatus
from typing import Tuple

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import tag

from account.factories import PASSWORD, UserFactory
from comment.models import DiaryComment
from diary.factory import DiaryFactory
from diary.models import Diary
from epuls_tools.scaler import PULS_FOR_ACTION
from epuls_tools.test import SimpleDBTestCase
from puls.factories import SinglePulsFactory
from puls.models import Puls, PulsType, SinglePuls

# TODO test for: CUDL


class DiaryDB(SimpleDBTestCase):
    @classmethod
    def setUpClass(cls):
        # main user has got 3 entries in Diary with one of them is hide.
        super(DiaryDB, cls).setUpClass()
        main_user = User.objects.first()
        DiaryFactory.create_batch(2, author=main_user)
        # Hide entry
        DiaryFactory(author=main_user, is_hide=True)

    def setUp(self):
        self.user = User.objects.first()
        self.client.login(username=self.user, password=PASSWORD)


@tag("v_dc")
class DiaryDetailViewTestCase(DiaryDB):
    def setUp(self):
        super(DiaryDetailViewTestCase, self).setUp()
        self.url = partial(reverse, "account:diary-detail")
        self.payload = {"comment": "test-comment"}

    def test_basic_test(self):
        """Should create 3 Diary instance"""
        self.assertEqual(Diary.objects.count(), 3)

    def test_user_is_able_visit_own_entry_on_diary(self):
        diary = Diary.objects.first()

        response = self.client.get(
            self.url(kwargs={"username": self.user.username, "pk": diary.pk})
        )

        diary_instance = response.context.get("object")

        self.assertEqual(diary, diary_instance)

    def test_user_is_able_visit_own_hide_entry(self):
        hide_diary = Diary.objects.first()

        response = self.client.get(
            self.url(kwargs={"username": self.user.username, "pk": hide_diary.pk})
        )

        diary_instance = response.context.get("object")

        self.assertEqual(hide_diary, diary_instance)

    def test_guest_should_not_see_hide_entry(self):
        last_user = User.objects.last()
        hide_diary = Diary.objects.first()

        self.client.logout()
        self.client.login(username=last_user.username, password=PASSWORD)

        response = self.client.get(
            self.url(kwargs={"username": self.user.username, "pk": hide_diary.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_should_post_new_comment(self):
        pk_diary = Diary.objects.first().pk

        self.client.post(
            self.url(kwargs={"pk": pk_diary, "username": self.user.username}),
            data=self.payload,
        )

        self.assertEqual(DiaryComment.objects.count(), 1)

        comment_instance = DiaryComment.objects.first()

        self.assertEqual(comment_instance.diary.pk, pk_diary)
        self.assertEqual(comment_instance.author, self.user)

    def test_should_not_get_any_puls_when_user_is_user_photo(self):
        pk_diary = Diary.objects.first().pk

        self.client.post(
            self.url(kwargs={"pk": pk_diary, "username": self.user.username}),
            data=self.payload,
        )

        self.assertFalse(SinglePuls.objects.filter(puls=self.user.profile.puls))

        user_puls = Puls.objects.filter(profile=self.user.profile).first().puls

        # user should have 0 Puls
        self.assertEqual(user_puls, 0)

    def create_new_user_with_diary(self) -> Tuple[UserFactory, DiaryFactory]:
        new_user = UserFactory()
        diary = DiaryFactory(author=new_user)

        return new_user, diary

    def test_should_give_away_puls_when_user_comment_photo_another_user(self):
        new_user, new_diary = self.create_new_user_with_diary()

        self.client.post(
            self.url(kwargs={"pk": new_diary.pk, "username": new_user.username}),
            data=self.payload,
        )

        single_puls = SinglePuls.objects.filter(
            puls=self.user.profile.puls
        )  # should be one

        self.assertEqual(single_puls.count(), 1)

        # points
        excepted_puls = PULS_FOR_ACTION[PulsType.COMMENT_ACTIVITY_DIARY]

        self.assertEqual(excepted_puls, single_puls.first().quantity)

    def test_should_give_away_puls_when_user_comment_photo_another_user_second_option(
        self,
    ):
        new_user, new_diary = self.create_new_user_with_diary()
        SinglePulsFactory(
            quantity=0.2,
            type=PulsType.COMMENT_ACTIVITY_PICTURE,
            puls=self.user.profile.puls,
        )

        self.client.post(
            self.url(kwargs={"pk": new_diary.pk, "username": new_user.username}),
            data=self.payload,
        )

        single_puls = SinglePuls.objects.filter(
            puls=self.user.profile.puls
        )  # should be one

        self.assertEqual(single_puls.count(), 2)

        # points
        excepted_puls = PULS_FOR_ACTION[PulsType.COMMENT_ACTIVITY_DIARY]

        self.assertEqual(excepted_puls, single_puls.first().quantity)
