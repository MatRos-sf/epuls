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

from .emotion import BasicEmotion, DivineEmotion, ProEmotion, XtremeEmotion

# paths
PROFILE_PICTURE_PATH = "profile_picture"

BASIC_TYPE = {
    "power": 0,
    "friends": 60,
    "best_friends": 0,
    "own_visitors": 5,
    "sb_visitors": 0,
    "picture": 5 * 1024 * 1024,
    "gallery": 1,
}
PRO_TYPE = {
    "power": 1,
    "friends": 80,
    "best_friends": 2,
    "own_visitors": 10,
    "sb_visitors": 5,
    "picture": 10 * 1024 * 1024,
    "gallery": 10,
}
XTREME_TYPE = {
    "power": 2,
    "friends": 130,
    "best_friends": 3,
    "own_visitors": 14,
    "sb_visitors": 10,
    "picture": 15 * 1024 * 1024,
    "gallery": 15,
}
DIVINE_TYPE = {
    "power": 3,
    "friends": 200,
    "best_friends": 4,
    "own_visitors": 14,
    "sb_visitors": 14,
    "picture": 1000 * 1024 * 1024,
    "gallery": 500,
}

TYPE_OF_PROFILE = {"B": BASIC_TYPE, "P": PRO_TYPE, "X": XTREME_TYPE, "D": DIVINE_TYPE}


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
    emotion = models.TextField(
        choices=[
            *BasicEmotion.choices,
            *ProEmotion.choices,
            *XtremeEmotion.choices,
            *DivineEmotion.choices,
        ],
        default=BasicEmotion.HAPPINESS,
    )

    # TODO country = models.CharField(max_length=)
    voivodeship = models.CharField(
        choices=VOIVODESHIP_CHOICES, max_length=100, blank=True, null=True
    )

    puls = models.OneToOneField(Puls, models.CASCADE, blank=True, null=True)

    # type of profile
    type_of_profile = models.TextField(
        choices=ProfileType.choices,
        default=ProfileType.BASIC,
        max_length=1,
        help_text="WARNING! To change the profile type correctly, please use the 'change_type_of_profile' method",
    )
    expire_of_tier = models.DateField(
        blank=True,
        null=True,
        help_text="When this field is empty, it means that the curren type of user account is BASIC. "
        "Otherwise, it indicates the expiration of the current profile type.",
    )

    # visitor
    male_visitor = models.IntegerField(default=0)
    female_visitor = models.IntegerField(default=0)

    amt_of_galleries = models.PositiveSmallIntegerField(default=0)
    size_of_pictures = models.PositiveIntegerField(
        default=0,
        help_text="Shows currently size of all pictures expressed by byte who belong to the particular user.",
    )

    __currently_type = None

    def __str__(self) -> str:
        return f"{self.user.username}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__currently_type = self.type_of_profile

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.__currently_type = self.type_of_profile

    def get_absolute_url(self) -> str:
        return reverse("account:profile", kwargs={"username": self.user.username})

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

    @property
    def currently_type(self) -> str:
        return str(self.__currently_type)

    def is_image_permitted(self, size: int) -> bool:
        return (self.size_of_pictures + size) < TYPE_OF_PROFILE[self.type_of_profile][
            "picture"
        ]

    def pull_field_limit(self, name_field):
        return TYPE_OF_PROFILE[self.type_of_profile].get(name_field, None)

    def add_friend(self, friend: User):
        if friend.pk != self.user.pk:
            max_amt_friends = TYPE_OF_PROFILE[self.type_of_profile]["friends"]
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
            if self.user.pk != friend.pk and friend.pk in self.friends.values_list(
                "pk", flat=True
            ):
                max_amt_best_friends = TYPE_OF_PROFILE[self.type_of_profile][
                    "best_friends"
                ]
                if self.best_friends.count() < max_amt_best_friends:
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

    def remove_best_friend(self, friend: User) -> None:
        self.best_friends.remove(friend)
        self.save()

    def set_profile_picture(self, image_field: ImageField) -> None:
        """
        Set a new profile picture.
        """
        self.profile_picture = image_field
        self.save(update_fields=["profile_picture"])

    def delete_profile_picture(self) -> None:
        self.profile_picture = None
        self.save(update_fields=["profile_picture"])

    def add_visitor(self, gender: str) -> NoReturn:
        """
        Updates the visitor count for a gender-specific field in the Profile model.
        """
        if gender in ["male", "female"]:
            # TODO -> different way ?
            Profile.objects.filter(pk=self.pk).update(
                **{f"{gender}_visitor": F(f"{gender}_visitor") + 1}
            )
            # visitor = getattr(self, f'{gender}_visitor')
            # visitor =
        else:
            raise ValueError("Gender must be 'male' or 'female'!")

    def change_type_of_profile(self, new_type: ProfileType = ProfileType.BASIC) -> None:
        power_of_old_type = TYPE_OF_PROFILE[self.type_of_profile]["power"]
        power_of_new_type = TYPE_OF_PROFILE[new_type]["power"]

        if power_of_old_type > power_of_new_type:
            self.revert_profile(TYPE_OF_PROFILE[new_type])
            self.change_default_emotion(new_type)

        self.type_of_profile = new_type
        self.save()

    def reduce_friends(self, max_amt: int) -> None:
        friends_to_delete = list(self.friends.all()[max_amt:])

        if friends_to_delete:
            self.friends.remove(*friends_to_delete)

    def reduce_best_friends(self, max_amt: int) -> None:
        bf_to_delete = list(self.best_friends.all()[max_amt:])

        if bf_to_delete:
            self.best_friends.remove(*bf_to_delete)

    def reduce_gallery(self, max_amt: int) -> None:
        galleries_to_delete = self.galleries.all().values_list("id", flat=True)[
            max_amt:
        ]

        if galleries_to_delete:
            from photo.models import Gallery

            Gallery.objects.filter(id__in=galleries_to_delete).delete()
            self.amt_of_galleries -= len(galleries_to_delete)

    def reduce_picture(self, max_amt: int) -> None:
        from photo.models import Picture

        id_pictures_to_delete = []
        reduce_size = self.size_of_pictures - max_amt

        for picture in Picture.objects.filter(gallery__profile=self):
            if reduce_size <= 0:
                break

            reduce_size -= picture.picture.size
            id_pictures_to_delete.append(picture.id)

        if id_pictures_to_delete:
            Picture.objects.filter(id__in=id_pictures_to_delete).delete()

        self.size_of_pictures = self.size_of_pictures - reduce_size

    def revert_profile(self, new_type):
        for key in new_type.keys():
            if key == "power":
                continue

            amt = new_type[key]
            field = getattr(self, "reduce_" + key)
            field(amt)

    def change_default_emotion(self, new_type):
        """
        Sets default emotions depending on profile_type. This method should be use when user change type of profile
        from high to lower.
        """
        match new_type:
            case "B":
                self.emotion = BasicEmotion.HAPPINESS
            case "P":
                self.emotion = ProEmotion.NEUTRALITY
            case "X":
                self.emotion = XtremeEmotion.CONFUSION


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


# __all__ = ['TYPE_OF_PROFILE', 'ProfileType', 'Gender', 'AboutUser', 'Profile','Visitor','FriendRequest']
