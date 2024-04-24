from django.contrib.auth.models import User
from django.db import models


class Comment(models.Model):
    """Abstract model represents comment section"""

    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.CharField(max_length=300)

    created = models.DateTimeField(auto_now_add=True)
    # TODO: status, report

    class Meta:
        abstract = True
        ordering = ["-created"]
