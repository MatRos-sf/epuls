from django.contrib.auth.models import User
from django.db import models


class Shouter(models.Model):
    """
    Model represent a Shouter.
    Shouter is a feature similar to a news ticker that allows user to present themselves.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(blank=True, null=True)
