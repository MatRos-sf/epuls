from django.core.files.base import ContentFile
from factory import Faker, LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory, ImageField

from account.factories import ProfileFactory, UserFactory

from .models import Gallery, Picture


class GalleryFactory(DjangoModelFactory):
    class Meta:
        model = Gallery

    name = Sequence(lambda n: f"gallery_{n}")
    description = Faker("sentence")
    profile = SubFactory(ProfileFactory)


class PictureFactory(DjangoModelFactory):
    class Meta:
        model = Picture

    title = Sequence(lambda n: f"photo_{n}")
    description = Faker("sentence")
    picture = ImageField(filename="test_picture.jpg")
    gallery = SubFactory(GalleryFactory)
    profile = SubFactory(ProfileFactory)
    presentation_tag = Sequence(lambda n: f"tag_{n}")
