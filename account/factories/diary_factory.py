from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from account.models import Diary

from .factories import UserFactory

__all__ = ["DiaryFactory"]


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = Faker("text")
    content = Faker("paragraph")
