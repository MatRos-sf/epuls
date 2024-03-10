from django.contrib import admin

from .models import Bonus, Puls, SinglePuls

admin.site.register(Puls)
admin.site.register(SinglePuls)
admin.site.register(Bonus)
