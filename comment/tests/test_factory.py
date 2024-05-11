from django.contrib.auth.models import User
from django.test import TestCase, tag

from account.factories import UserFactory
from comment.factories import PhotoCommentFactory
from comment.models import PhotoComment
from photo.factories import GalleryFactory, PictureFactory


@tag("f_pc")
class PhotoCommentFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for _ in range(3):
            user = UserFactory()
            gallery = GalleryFactory(profile=user.profile)
            picture = PictureFactory(gallery=gallery, profile=user.profile)

            PhotoCommentFactory(photo=picture, author=user)

    def test_should_create_3_comments(self):
        self.assertEqual(PhotoComment.objects.count(), 3)
