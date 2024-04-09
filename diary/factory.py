from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from account.factories import UserFactory

from .models import Diary

__all__ = ["DiaryFactory"]


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = Faker("text")
    content = Faker("paragraph")
