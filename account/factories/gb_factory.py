from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from account.models import Guestbook

from .factories import UserFactory

__all__ = ["GuestbookFactory"]


class GuestbookFactory(DjangoModelFactory):
    class Meta:
        model = Guestbook

    sender = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
    entry = Faker("text")
