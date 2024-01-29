from django.contrib import admin

from .models.profile import AboutUser, Profile

admin.site.register(Profile)
admin.site.register(AboutUser)
