from django.db import models
from django.contrib.auth.models import User


class ProfileType(models.TextChoices):
    BASIC = "B", "Basic"
    PRO = "P", "Pro"
    XTREME = "X", "Xtreme"
    DIVINE = "D", "Divine"


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)

    short_description = models.TextField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    type_of_profile = models.TextField(choices=ProfileType.choices, default=ProfileType.BASIC, max_length=1)
    created = models.DateTimeField(auto_now_add=True)

    # https://django-localflavor.readthedocs.io/en/latest/localflavor/pl/#localflavor.pl.pl_voivodeships.VOIVODESHIP_CHOICES
    #country =
    #voivodeship =

