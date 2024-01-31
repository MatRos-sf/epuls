from django.contrib import admin

from .models import AboutUser, Diary, Guestbook, Profile

admin.site.register(Profile)
admin.site.register(AboutUser)
admin.site.register(Guestbook)
admin.site.register(Diary)
