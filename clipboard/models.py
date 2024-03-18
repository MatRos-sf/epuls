from django.contrib.auth.models import User
from django.db import models


class Clipboard(models.Model):
    """
    Model representing a user's clipboard. It is created when a user changes their profile type from higher to lower.

    Clipboard stores:
        - recently added friends with Profile models
        - recently added best friend with Profile models

    Additionally, the model has an expiry date set to 31 days. If the user doesn't update their profile type within this period, the clipboard will be destroyed.
    """

    owner = models.OneToOneField("account.Profile", on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    # expiry = models.DateField(blank=True, null=True)

    # Profile fields
    friends = models.ManyToManyField(User, related_name="clipboard_friends", blank=True)
    best_friends = models.ManyToManyField(
        User, related_name="clipboard_best_friends", blank=True
    )

    def update_clipboard(self, payload):
        for key, value in payload.items():
            field = getattr(self, key)
            print(field)
            field.add(*value)
