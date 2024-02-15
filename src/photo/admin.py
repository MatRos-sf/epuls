from django.contrib import admin

from .models import Gallery, Picture, ProfilePicture

admin.site.register(ProfilePicture)
admin.site.register(Picture)
admin.site.register(Gallery)
