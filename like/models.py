from django.conf import settings
from django.db import models

from comment.models import PhotoComment


class AbstractLike(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.active = False
        self.save()


# https://stackoverflow.com/questions/62879957/how-to-implement-a-like-system-in-django-templates
class LikePhotoComment(AbstractLike):
    comment = models.ForeignKey(
        PhotoComment, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = ["comment", "user"]

    def __str__(self):
        return (
            f"{self.user.username} liked comment {self.comment.id} at {self.timestamp}"
        )


# class LikePhoto(AbstractLike):
#     photo = models.ForeignKey('photo.Picture', on_delete=models.CASCADE, related_name='likes')
#
#     def __str__(self):
#         return f"{self.user.username} liked photo {self.photo.id} at {self.timestamp}"
