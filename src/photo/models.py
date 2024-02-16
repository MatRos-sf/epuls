from django.contrib.auth.models import User
from django.db import models


class ProfilePicture(models.Model):
    picture = models.ImageField(upload_to="profile_picture", default="default.jpg")

    is_accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)


class Gallery(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class Picture(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    picture = models.ImageField(upload_to="picture")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    # likes
