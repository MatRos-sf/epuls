from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile, AboutUser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        about_user = AboutUser.objects.create()
        Profile.objects.create(user=instance, about_me=about_user)
