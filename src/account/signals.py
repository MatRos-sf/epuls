from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from photo.models import ProfilePicture

from .models.profile import AboutUser, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # when user is created should also create AboutUser, ProfilePicture
    if created:
        about_user = AboutUser.objects.create()
        profile_picture = ProfilePicture.objects.create()

        Profile.objects.create(
            user=instance, about_me=about_user, profile_picture=profile_picture
        )
