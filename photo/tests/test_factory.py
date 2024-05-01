import os

from django.test import TestCase, tag

from account.factories import UserFactory
from account.models import Profile
from photo.factories import GalleryFactory, PictureFactory
from photo.models import Gallery, Picture, Stats


@tag("f_g")
class GalleryFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(GalleryFactoryTestCase, cls).setUpClass()
        user = UserFactory()
        GalleryFactory.create_batch(2, profile=user.profile)

    def test_should_create_1_profile_model(self):
        self.assertEqual(Profile.objects.count(), 1)

    def test_should_add_sample_sentence_in_description_field(self):
        gallery = Gallery.objects.first()

        self.assertIsInstance(gallery.description, str)

    def test_should_create_2_gallery(self):
        self.assertEqual(Gallery.objects.count(), 2)

    def test_should_trigger_signals_and_create_stats(self):
        self.assertEqual(Stats.objects.count(), 2)


class PictureFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PictureFactoryTestCase, cls).setUpClass()
        user = UserFactory()
        gallery = GalleryFactory(profile=user.profile)
        PictureFactory.create_batch(3, gallery=gallery, profile=user.profile)

    @classmethod
    def tearDownClass(cls):
        url_pictures_to_del = [
            picture.picture.path for picture in Picture.objects.all()
        ]

        for path in url_pictures_to_del:
            if os.path.exists(path):
                os.remove(path)

        super(PictureFactoryTestCase, cls).tearDownClass()

    def test_should_create_three_picture_models(self):
        self.assertEqual(Picture.objects.count(), 3)

    @tag("f_pf")
    def test_should_trigger_signals_and_create_stats(self):
        """
        Should create 4 Stats models:
            * 1 Gallery stats
            * 3 Picture stats
        :return:
        """
        self.assertEqual(Stats.objects.count(), 4)
