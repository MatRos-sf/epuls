from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from photo.factories import PictureFactory

from .models import PhotoComment


class PhotoCommentFactory(DjangoModelFactory):
    class Meta:
        model = PhotoComment

    photo = SubFactory(PictureFactory)
