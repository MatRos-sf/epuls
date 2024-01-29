from django.contrib.auth.models import User
from django.db import models


class Guestbook(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The person who types something.",
        related_name="sent_gb_entry",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The person who receive message.",
        related_name="received_gb_entry",
    )
    entry = models.TextField(help_text="Say hello!")
    created = models.DateTimeField(auto_now_add=True)
