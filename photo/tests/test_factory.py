from django.test import TestCase, tag

from account.factories import UserFactory
from account.models import Profile
from photo.factories import GalleryFactory
from photo.models import Gallery


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
