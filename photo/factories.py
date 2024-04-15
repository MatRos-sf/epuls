from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from account.factories import ProfileFactory, UserFactory

from .models import Gallery


class GalleryFactory(DjangoModelFactory):
    class Meta:
        model = Gallery

    name = Sequence(lambda n: f"gallery_{n}")
    description = Faker("sentence")
    profile = SubFactory(ProfileFactory)
