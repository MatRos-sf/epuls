from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from account.models.profile import PROFILE_PICTURE_PATH
from epuls_tools.scaler import give_away_puls
from puls.models import PulsType


class ProfilePictureRequest(models.Model):
    picture = models.ImageField(
        upload_to=PROFILE_PICTURE_PATH, verbose_name="profile picture"
    )
    profile = models.ForeignKey("account.Profile", on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    examination_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs) -> None:
        super(ProfilePictureRequest, self).save(*args, **kwargs)

        # TODO celery
        img = Image.open(self.picture.path)
        if img.height > 300 or img.width > 300:
            max_size = (300, 300)
            img.thumbnail(max_size)
            img.save(self.picture.path)

    def accept(self) -> None:
        """
        This method is used when an admin wants to accept a profile picture. When triggered, it performs the following actions:
            - Sets 'is_accepted' to True.
            - Updates 'examination_date' to the current time when the picture was accepted.
            - Sets the accepted picture as the profile picture.
            - Give a pulse if the user doesn't have one yet.
        """
        self.is_accepted = True
        self.examination_date = timezone.now()
        self.save()

        # update profile photo
        self.profile.set_profile_picture(self.picture)
        # TODO notification about accept

        if not self.profile.puls.check_is_value_set(PulsType.PROFILE_PHOTO):
            give_away_puls(user_profile=self.profile, type=PulsType.PROFILE_PHOTO)

    def reject(self) -> None:
        """
        This method is used when an admin wants to reject a profile picture.
        """
        self.is_rejected = True
        self.examination_date = timezone.now()
        self.save()
        # TODO notification about reject


class Gallery(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    profile = models.ForeignKey(
        "account.Profile", on_delete=models.CASCADE, related_name="galleries"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    # is_private = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse(
            "photo:gallery-detail",
            kwargs={"username": self.profile.user.username, "pk": self.pk},
        )


class Picture(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    picture = models.ImageField(upload_to="picture")
    gallery = models.ForeignKey(
        Gallery, on_delete=models.CASCADE, related_name="pictures"
    )
    profile = models.ForeignKey("account.Profile", on_delete=models.CASCADE)  # to del
    date_created = models.DateTimeField(auto_now_add=True)

    presentation_tag = models.CharField(
        max_length=50,
        help_text="Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )

    class Meta:
        ordering = ["-date_created"]
        unique_together = [["title", "profile"]]

    # TODO likes

    def clean(self):
        picture_size = self.picture.size

        if not self.gallery.profile.is_image_permitted(picture_size):
            raise ValidationError(
                {
                    "picture": _(
                        "Picture is too big. Change picture or update your profile type."
                    )
                }
            )

    def get_absolute_url(self):
        return reverse("photo:picture-detail", kwargs={"pk": self.pk})


class Stats(models.Model):
    """Abstract model represents statistics."""

    amt_comments = models.IntegerField(default=0)
    amt_likes = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    popularity = models.GeneratedField(
        expression=F("amt_comments") + F("amt_likes") + F("total_views"),
        output_field=models.IntegerField(),
        db_persist=True,
        help_text="Calculated as the sum of comments, likes, and views.",
    )

    class Meta:
        abstract = True
        verbose_name_plural = "Stats"


class GalleryStat(Stats):
    """Model representing statistic for a Gallery"""

    gallery = models.OneToOneField(
        Gallery, on_delete=models.CASCADE, related_name="stats"
    )

    @property
    def amt_pictures(self):
        return self.gallery.pictures.count()


class PictureStats(Stats):
    """Model representing statistic for a picture."""

    picture = models.OneToOneField(
        Picture, on_delete=models.CASCADE, related_name="stats"
    )
