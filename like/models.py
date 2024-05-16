from django.conf import settings
from django.db import models


class AbstractLike(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.active = False
        self.save()
