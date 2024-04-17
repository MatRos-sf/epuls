from django.contrib import admin

from .models import AboutUser, FriendRequest, Profile, Visitor

admin.site.register(AboutUser)
admin.site.register(Visitor)
admin.site.register(FriendRequest)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_confirm")
    ordering = ("is_confirm",)
