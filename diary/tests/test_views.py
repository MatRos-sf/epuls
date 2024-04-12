from functools import partial

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import tag

from account.factories import PASSWORD
from diary.factory import DiaryFactory
from diary.models import Diary
from epuls_tools.test import SimpleDBTestCase

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


class DiaryDetailViewTestCase(DiaryDB):
    def setUp(self):
        super(DiaryDetailViewTestCase, self).setUp()
        self.url = partial(reverse, "account:diary-detail")

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

    @tag("v_dc")
    def test_guest_should_not_see_hide_entry(self):
        last_user = User.objects.last()
        hide_diary = Diary.objects.first()

        self.client.logout()
        self.client.login(username=last_user.username, password=PASSWORD)

        response = self.client.get(
            self.url(kwargs={"username": self.user.username, "pk": hide_diary.pk})
        )

        diary_instance = response.context.get("object")

        self.assertIsNone(diary_instance)
