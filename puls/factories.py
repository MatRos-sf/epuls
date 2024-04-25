"""
     Factory for:
        - Puls model
        - Single Puls
"""
from random import choice

from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from puls.models import Puls, PulsType, SinglePuls


class PulsFactory(DjangoModelFactory):
    class Meta:
        model = Puls


class SinglePulsFactory(DjangoModelFactory):
    class Meta:
        model = SinglePuls

    quantity = Faker("pyint", min_value=1, max_value=10)
    puls = SubFactory(PulsFactory)
