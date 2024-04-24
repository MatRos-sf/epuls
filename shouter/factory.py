from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from account.factories import UserFactory

from .models import Shouter


class ShouterFactory(DjangoModelFactory):
    class Meta:
        model = Shouter

    user = SubFactory(UserFactory)
    text = Faker("sentence")
