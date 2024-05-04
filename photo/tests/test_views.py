from datetime import timedelta
from functools import partial
from typing import Tuple
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from account.factories import PASSWORD, UserFactory
from comment.models import PhotoComment
from epuls_tools.scaler import PULS_FOR_ACTION
from photo.factories import GalleryFactory, PictureFactory
from photo.models import Gallery, GalleryStats, Picture, PictureStats
from puls.models import Puls, PulsType, SinglePuls


class PictureDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = UserFactory()
        gallery = GalleryFactory(profile=user.profile)
        PictureFactory(gallery=gallery, profile=user.profile)

    def setUp(self):
        self.user = User.objects.first()
        self.client.login(username=self.user.username, password=PASSWORD)
        self.url = partial(reverse, "photo:picture-detail")

        self.payload = {"comment": "test-comment"}

    def test_dataset(self):
        self.assertTrue(User.objects.count())
        self.assertTrue(Gallery.objects.count())
        self.assertTrue(Picture.objects.count())

    def test_should_post_new_comment(self):
        pk_picture = Picture.objects.first().pk
        self.client.post(self.url(kwargs={"pk": pk_picture}), data=self.payload)

        self.assertEqual(PhotoComment.objects.count(), 1)

        comment_instance = PhotoComment.objects.first()

        self.assertEqual(comment_instance.photo.pk, pk_picture)
        self.assertEqual(comment_instance.author, self.user)

    def test_should_not_get_any_puls_when_user_is_user_photo(self):
        pk_picture = Picture.objects.first().pk
        self.client.post(self.url(kwargs={"pk": pk_picture}), data=self.payload)

        self.assertFalse(SinglePuls.objects.filter(puls=self.user.profile.puls))
        user_puls = Puls.objects.filter(profile=self.user.profile).first().puls

        # user should have 0 Puls
        self.assertEqual(user_puls, 0)

    def create_new_user_with_picture(self) -> Tuple[UserFactory, PictureFactory]:
        new_user = UserFactory()
        gallery = GalleryFactory(profile=new_user.profile)
        picture = PictureFactory(gallery=gallery, profile=new_user.profile)

        return new_user, picture

    def test_should_give_away_puls_when_user_comment_photo_another_user(self):
        _, new_picture = self.create_new_user_with_picture()

        self.client.post(self.url(kwargs={"pk": new_picture.pk}), data=self.payload)

        single_puls = SinglePuls.objects.filter(
            puls=self.user.profile.puls
        )  # should be one

        self.assertEqual(single_puls.count(), 1)
        # points
        excepted_puls = PULS_FOR_ACTION[PulsType.COMMENT_ACTIVITY]

        self.assertEqual(excepted_puls, single_puls.first().quantity)

    def test_should_create_only_one_single_puls(self):
        _, new_picture = self.create_new_user_with_picture()

        for _ in range(3):
            self.client.post(self.url(kwargs={"pk": new_picture.pk}), data=self.payload)

        self.assertEqual(SinglePuls.objects.count(), 1)

    def test_should_not_create_single_puls_when_comment_gap_is_to_short(self):
        _, new_picture = self.create_new_user_with_picture()
        mock_date = timezone.now() - timedelta(days=3)
        comment_gap = 4  # minutes

        # mock auto create date
        with patch("django.utils.timezone.now", Mock(return_value=mock_date)):
            self.client.post(self.url(kwargs={"pk": new_picture.pk}), data=self.payload)

        # try to get puls for 4 minutes after comment
        with patch(
            "django.utils.timezone.now",
            Mock(return_value=mock_date + timedelta(minutes=comment_gap)),
        ):
            self.client.post(self.url(kwargs={"pk": new_picture.pk}), data=self.payload)

        self.assertEqual(SinglePuls.objects.count(), 1)

    def test_should_change_stats_when_was_add_comment(self):
        _, picture = self.create_new_user_with_picture()

        self.client.post(self.url(kwargs={"pk": picture.pk}), data=self.payload)

        gallery_popularity = GalleryStats.objects.get(
            gallery__pk=picture.gallery.pk
        ).popularity
        picture_popularity = PictureStats.objects.get(pk=picture.pk).popularity
        self.assertEqual(gallery_popularity, 1)
        self.assertEqual(picture_popularity, 1)
        self.assertEqual(PhotoComment.objects.count(), 1)
