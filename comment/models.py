from django.contrib.auth.models import User
from django.db import models

from diary.models import Diary
from photo.models import Picture


class Comment(models.Model):
    """Abstract model represents comment section"""

    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.CharField(max_length=300)

    created = models.DateTimeField(auto_now_add=True)
    # TODO: status, report

    class Meta:
        abstract = True
        ordering = ["-created"]


# TODO: subcomment
class PhotoComment(Comment):
    photo = models.ForeignKey(
        Picture, on_delete=models.CASCADE, related_name="photo_comments"
    )


class DiaryComment(Comment):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="diary_comments"
    )
