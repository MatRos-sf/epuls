from django.contrib import admin

from .models import Gallery, GalleryStats, Picture, PictureStats, ProfilePictureRequest

admin.site.register(ProfilePictureRequest)
admin.site.register(Picture)
admin.site.register(Gallery)
admin.site.register(GalleryStats)
admin.site.register(PictureStats)
