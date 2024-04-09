from django.contrib import admin

from .models import AboutUser, FriendRequest, Profile, Visitor

admin.site.register(Profile)
admin.site.register(AboutUser)
admin.site.register(Visitor)
admin.site.register(FriendRequest)
