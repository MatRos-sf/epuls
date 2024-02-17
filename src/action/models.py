from django.contrib.auth.models import User
from django.db import models


class Action(models.Model):
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    whom = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="whom_actions",
    )
    message = models.CharField(max_length=100, blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)
