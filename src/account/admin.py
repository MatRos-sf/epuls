from django.contrib import admin

from .models import AboutUser, Guestbook, Profile

admin.site.register(Profile)
admin.site.register(AboutUser)
admin.site.register(Guestbook)
