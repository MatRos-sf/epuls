from django.contrib.auth.models import User
from django.db import models


class ActionMessage(models.TextChoices):
    OWN_PROFILE = "own_profile", "OWN_PROFILE"
    SB_PROFILE = "sb_profile", "SB_PROFILE"
    OWN_GUESTBOOK = "own_guestbook", "OWN_GUESTBOOK"
    SB_GUESTBOOK = "sb_guestbook", "SB_GUESTBOOK"
    OWN_DIARY = "own_diary", "OWN_DIARY"


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
    def last_user_action(cls, who: User) -> "Action":
        return cls.objects.filter(who=who).first()
