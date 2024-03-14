from datetime import timedelta
from typing import NoReturn, Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Max
from django.db.models.fields.files import ImageField
from django.forms import ValidationError
from django.urls import reverse
from django.utils import timezone
from localflavor.pl.pl_voivodeships import VOIVODESHIP_CHOICES

from puls.models import Puls

# paths
PROFILE_PICTURE_PATH = "profile_picture"
AMOUNT_OF_BEST_FRIENDS = {"P": 5, "X": 10, "D": 20}
AMOUNT_OF_FRIENDS = {"B": 60, "P": 80, "X": 130, "D": 200}


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

    is_set = models.BooleanField(
        default=False,
        help_text="This field is true when all of the fields are filled up.",
    )

    def check_model_is_fill_up(self) -> bool:
        """
        Checks whether is_set True. If the field False, then checks if the fields are fill up.
        """
        if self.is_set:
            return True
        else:
            fields_name = [
                field.name
                for field in AboutUser._meta.get_fields()
                if field.name not in ("profile", "id", "is_set")
            ]
            is_fields_set = [getattr(self, i) for i in fields_name]

            if all(is_fields_set):
                self.is_set = True
                self.save(update_fields=["is_set"])
                return True

        return False


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.TextField(choices=Gender.choices, default=Gender.MALE)
    date_of_birth = models.DateField(blank=True, null=True)

    short_description = models.TextField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    about_me = models.OneToOneField(
        AboutUser, on_delete=models.CASCADE, blank=True, null=True
    )

    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    best_friends = models.ManyToManyField(User, blank=True, related_name="best_friends")

    is_confirm = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to="profile_picture", blank=True, null=True
    )

    # country = models.CharField(max_length=)
    voivodeship = models.CharField(
        choices=VOIVODESHIP_CHOICES, max_length=100, blank=True, null=True
    )

    puls = models.OneToOneField(Puls, models.CASCADE, blank=True, null=True)

    # type of profile
    type_of_profile = models.TextField(
        choices=ProfileType.choices, default=ProfileType.BASIC, max_length=1
    )
    expire_of_tier = models.DateField(
        blank=True,
        null=True,
        help_text="When this field is empty, it means that the curren type of user account is BASIC. Otherwise, it indicates the expiration of the current profile type.",
    )

    # visitor
    male_visitor = models.IntegerField(default=0)
    female_visitor = models.IntegerField(default=0)

    @property
    def count_visitors(self) -> int:
        return self.male_visitor + self.female_visitor

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

    def get_absolute_url(self):
        return reverse("account:profile", kwargs={"username": self.user.username})

    def add_friend(self, friend: User):
        if friend.pk != self.user.pk:
            max_amt_friends = AMOUNT_OF_FRIENDS[self.type_of_profile]
            if self.friends.count() < max_amt_friends:
                self.friends.add(friend)
                self.save()
            else:
                raise ValidationError("Your list of friends is too large.")

    def remove_friend(self, friend: User):
        self.friends.remove(friend)
        self.save()

    def add_best_friend(self, friend: User):
        if self.type_of_profile != "B":
            if self.user.pk != friend.pk and friend.pk in self.friends:
                max_amt_best_friends = AMOUNT_OF_BEST_FRIENDS[self.type_of_profile]
                if self.best_friends.count() <= max_amt_best_friends:
                    self.best_friends.add(friend)
                    self.save()
                else:
                    raise ValidationError(
                        "You have the maximum amount of best friends!"
                    )
            else:
                raise ValidationError(
                    "You cannot add best friend if friend is not in your friends list or you are the best friend"
                )
        else:
            raise ValidationError(
                "You cannot add best friend because you have a basic account!"
            )

    def remove_best_friend(self, friend):
        self.friends.remove(friend)
        self.save()

    def set_profile_picture(self, image_field: ImageField) -> None:
        """
        Set a new profile picture.
        """
        self.profile_picture = image_field
        self.save(update_fields=["profile_picture"])

    def delete_profile_picture(self) -> None:
        print(self.profile_picture.path)
        self.profile_picture = None
        self.save(update_fields=["profile_picture"])

    def add_visitor(self, gender: str) -> NoReturn:
        """
        Updates the visitor count for a gender-specific field in the Profile model.
        """
        if gender in ["male", "female"]:
            Profile.objects.filter(pk=self.pk).update(
                **{f"{gender}_visitor": F(f"{gender}_visitor") + 1}
            )
        else:
            raise ValueError("Gender must be 'male' or 'female'!")

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

    @classmethod
    def get_visitor(cls, user: User, amt: int = 5):
        """
        Returns a qs of usernames for visitors who have visited the user's profile.
        """
        return (
            cls.objects.filter(receiver=user)
            .exclude(visitor=user)
            .values("visitor")
            .annotate(max_date=Max("date_of_visit"))
            .order_by("-max_date")
            .values_list(
                "visitor__username",
                "visitor__profile__gender",
                "visitor__profile__type_of_profile",
                "visitor__profile__profile_picture",
            )[:amt]
        )


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User, related_name="from_user", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE)

    def accept(self) -> bool:
        try:
            self.from_user.profile.add_friend(self.to_user)
            self.to_user.profile.add_friend(self.from_user)
        except ValidationError:
            return False
        return True

    # def save(self, *args, **kwargs):
    #     if self.is_accepted:
    #         try:
    #             self.from_user.profile.add_friend(self.to_user)
    #             self.to_user.profile.add_friend(self.from_user)
    #         except ValidationError:
    #             ...
    #     super().save(*args, **kwargs)
