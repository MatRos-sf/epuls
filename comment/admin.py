from django.contrib import admin

from .models import DiaryComment, PhotoComment

admin.site.register(PhotoComment)
admin.site.register(DiaryComment)
