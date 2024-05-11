from typing import Optional

from django.contrib.auth.models import User
from django.db import models


class ActionMessage(models.TextChoices):
    OWN_PROFILE = "own_profile", "OWN_PROFILE"
    SB_PROFILE = "sb_profile", "SB_PROFILE"

    OWN_GUESTBOOK = "own_guestbook", "OWN_GUESTBOOK"
    SB_GUESTBOOK = "sb_guestbook", "SB_GUESTBOOK"

    OWN_DIARY = "own_diary", "OWN_DIARY"
    SB_DIARY = "sb_diary", "SB_DIARY"

    OWN_FRIENDS = "own_friends", "OWN_FRIENDS"
    SB_FRIENDS = "sb_friends", "OWN_FRIENDS"

    OWN_GALLERY = "own_gallery", "OWN_GALLERY"
    SB_GALLERY = "sb_gallery", "SB_GALLERY"

    OWN_PHOTO = "own_photo", "OWN_PHOTO"
    SB_PHOTO = "sb_photo", "SB_PHOTO"

    OWN_PULS = "own_puls", "OWN_PULS"
    SB_PULS = "sb_puls", "SB_PULS"


class Action(models.Model):
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    whom = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="whom_actions",
    )
    # message = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(
        max_length=40, choices=ActionMessage.choices, blank=True, null=True
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    # https://stackoverflow.com/questions/44640479/type-annotation-for-classmethod-returning-instance
    @classmethod
    def last_user_action(cls, who: User) -> Optional["Action"]:
        return cls.objects.filter(who=who).first()
