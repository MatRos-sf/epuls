from django.contrib import admin

from .models import Gallery, Picture, ProfilePictureRequest

admin.site.register(ProfilePictureRequest)
admin.site.register(Picture)
admin.site.register(Gallery)
