from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from puls.models import Puls

from .models.profile import AMOUNT_OF_FRIENDS, AboutUser, Profile

POWER_OF_PROFILE_TYPE = {"B": 0, "P": 1, "X": 2, "D": 3}


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # when user is created should also create AboutUser, Puls
    if created:
        about_user = AboutUser.objects.create()
        puls = Puls.objects.create()
        Profile.objects.create(user=instance, about_me=about_user, puls=puls)
