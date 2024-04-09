from django.contrib import admin

from .models import AboutUser, FriendRequest, Guestbook, Profile, Visitor

admin.site.register(Profile)
admin.site.register(AboutUser)
admin.site.register(Guestbook)
admin.site.register(Visitor)
admin.site.register(FriendRequest)
