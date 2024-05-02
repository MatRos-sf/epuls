import os

from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from account.models import Profile

from .models import Gallery, GalleryStats, Picture, PictureStats


# Picture Signals
@receiver(post_save, sender=Picture)
def create_stats_instance_on_picture(sender, instance, created, **kwargs):
    if created:
        PictureStats.objects.create(picture=instance)


@receiver(post_delete, sender=Picture)
def delete_picture(sender, instance, **kwargs) -> None:
    """
    Removes image when models was deleted.
    """
    old_instance = instance.picture

    if os.path.exists(old_instance.path):
        # Update Profile
        Profile.objects.filter(user=instance.gallery.profile.user).update(
            size_of_pictures=F("size_of_pictures") - old_instance.size
        )

        os.remove(old_instance.path)


@receiver(pre_save, sender=Picture)
def delete_picture_when_updated(sender, instance, **kwargs) -> None:
    """
    Deletes old picture when user update the new one.
    """
    if not instance.pk:
        return

    old_instance = Picture.objects.get(pk=instance.pk)

    old_picture = old_instance.picture
    new_picture = instance.picture

    # if user's change photo then delete old one.
    if old_picture.path != new_picture.path:
        if os.path.exists(old_picture.path):
            old_size = old_picture.size
            new_size = new_picture.size
            os.remove(old_picture.path)

            Profile.objects.filter(user=instance.gallery.profile.user).update(
                size_of_pictures=F("size_of_pictures") - old_size + new_size
            )


# Gallery signal
@receiver(post_save, sender=Gallery)
def create_stats_instance_on_gallery(sender, instance, created, **kwargs):
    if created:
        GalleryStats.objects.create(gallery=instance)
