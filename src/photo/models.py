from django.db import models
from django.utils import timezone
from PIL import Image


class ProfilePictureRequest(models.Model):
    picture = models.ImageField(
        upload_to="profile_picture_request", verbose_name="profile picture"
    )

    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    examination_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs) -> None:
        super(ProfilePictureRequest, self).save(*args, **kwargs)

        img = Image.open(self.picture.path)
        if img.height > 300 or img.width > 300:
            max_size = (300, 300)
            img.thumbnail(max_size)
            img.save(self.picture.path)

    def accept(self):
        self.is_accepted = True
        self.examination_date = timezone.now()

    def reject(self):
        self.is_rejected = True
        self.examination_date = timezone.now()


class Gallery(models.Model):
    name = models.CharField(max_length=100)
    profile = models.ForeignKey("account.Profile", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class Picture(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    picture = models.ImageField(upload_to="picture")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    profile = models.ForeignKey("account.Profile", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    # likes
