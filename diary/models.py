from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Diary(models.Model):
    """Model representing a single entry in the diary."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    is_hide = models.BooleanField(
        default=False,
        verbose_name="hide",
        help_text="If set to true, only you are able to visit this entry.",
    )

    class Meta:
        ordering = ("-created",)

    def get_absolute_url(self):
        return reverse(
            "account:diary-detail",
            kwargs={"username": self.author.username, "pk": self.pk},
        )
