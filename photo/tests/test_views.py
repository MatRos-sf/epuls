from functools import partial

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase, tag

from account.factories import PASSWORD, UserFactory
from comment.models import PhotoComment
from photo.factories import GalleryFactory, PictureFactory
from photo.models import Gallery, Picture


@tag("pdv_ts")
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

    def test_dataset(self):
        self.assertTrue(User.objects.count())
        self.assertTrue(Gallery.objects.count())
        self.assertTrue(Picture.objects.count())

    def test_should_post_new_comment(self):
        comment = {"comment": "test-comment"}
        pk_picture = Picture.objects.first().pk
        self.client.post(self.url(kwargs={"pk": pk_picture}), data=comment)

        self.assertEqual(PhotoComment.objects.count(), 1)

        comment_instance = PhotoComment.objects.first()

        self.assertEqual(comment_instance.photo.pk, pk_picture)
        self.assertEqual(comment_instance.author, self.user)
