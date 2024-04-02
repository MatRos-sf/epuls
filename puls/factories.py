"""
     Factory for:
        - Puls model
"""
from factory.django import DjangoModelFactory

from puls.models import Puls


class PulsFactory(DjangoModelFactory):
    class Meta:
        model = Puls
