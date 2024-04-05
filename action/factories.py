from factory import SubFactory
from factory.django import DjangoModelFactory

from account.factories import UserFactory

from .models import Action


class ActionFactory(DjangoModelFactory):
    class Meta:
        model = Action

    who = SubFactory(UserFactory)
    whom = SubFactory(UserFactory)
