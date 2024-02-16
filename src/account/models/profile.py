from django.contrib.auth.models import User
from django.db import models


class ProfileType(models.TextChoices):
    BASIC = "B", "Basic"
    PRO = "P", "Pro"
    XTREME = "X", "Xtreme"
    DIVINE = "D", "Divine"


class AboutUser(models.Model):
    height = models.CharField(max_length=50, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    politics = models.CharField(max_length=50, blank=True, null=True)
    dish = models.CharField(max_length=50, blank=True, null=True)
    film = models.CharField(max_length=50, blank=True, null=True)
    song = models.CharField(max_length=50, blank=True, null=True)
    idol = models.CharField(max_length=50, blank=True, null=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
        upload_to="profile_picture", default="default_photo_picture.jpg"
    )

    # xyz = models.CharField(blank=True, null=True)
    # https://django-localflavor.readthedocs.io/en/latest/localflavor/pl/#localflavor.pl.pl_voivodeships.VOIVODESHIP_CHOICES
    # country =
    # voivodeship =

    def add_friends(self, friend: User):
        if friend.pk != self.pk:
            self.friends.add(friend)

        self.save()

    def remove_friends(self, friend: User):
        self.friends.remove(friend)
        self.save()


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
