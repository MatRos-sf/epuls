from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.files import ImageField
from django.utils import timezone
from localflavor.pl.pl_voivodeships import VOIVODESHIP_CHOICES

from puls.models import Puls

# paths
PROFILE_PICTURE_PATH = "profile_picture"
DEFAULT_PROFILE_PICTURE = "profile_picture/default_photo_picture.jpg"


class ProfileType(models.TextChoices):
    BASIC = "B", "Basic"
    PRO = "P", "Pro"
    XTREME = "X", "Xtreme"
    DIVINE = "D", "Divine"


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"


class AboutUser(models.Model):
    height = models.CharField(max_length=50, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    politics = models.CharField(max_length=50, blank=True, null=True)
    dish = models.CharField(max_length=50, blank=True, null=True)
    film = models.CharField(max_length=50, blank=True, null=True)
    song = models.CharField(max_length=50, blank=True, null=True)
    idol = models.CharField(max_length=50, blank=True, null=True)

    def is_set(self) -> bool:
        return all(
            [
                self.height,
                self.weight,
                self.politics,
                self.dish,
                self.film,
                self.song,
                self.idol,
            ]
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.TextField(choices=Gender.choices, default=Gender.MALE)
    date_of_birth = models.DateField(blank=True, null=True)

    short_description = models.TextField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    type_of_profile = models.TextField(
        choices=ProfileType.choices, default=ProfileType.BASIC, max_length=1
    )
    created = models.DateTimeField(auto_now_add=True)

    about_me = models.OneToOneField(
        AboutUser, on_delete=models.CASCADE, blank=True, null=True
    )

    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    is_confirm = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to="profile_picture", default=DEFAULT_PROFILE_PICTURE
    )

    # country = models.CharField(max_length=)
    voivodeship = models.CharField(
        choices=VOIVODESHIP_CHOICES, max_length=100, blank=True, null=True
    )

    puls = models.OneToOneField(Puls, models.CASCADE, blank=True, null=True)

    @property
    def age(self) -> Optional[int]:
        """
        Returns the age of the user.
        When date_of_birth is empty then return None.
        """
        if not self.date_of_birth:
            return
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def add_friends(self, friend: User):
        if friend.pk != self.pk:
            self.friends.add(friend)

        self.save()

    def remove_friends(self, friend: User):
        self.friends.remove(friend)
        self.save()

    def set_profile_picture(self, image_field: ImageField) -> None:
        """
        Set a new profile picture.
        """
        self.profile_picture = image_field
        self.save()

    def __str__(self):
        return f"{self.user.username}"


class Visitor(models.Model):
    date_of_visit = models.DateTimeField(auto_now_add=True)
    visitor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user who visited someone profile.",
        related_name="visitors",
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="The user who had been visited."
    )
