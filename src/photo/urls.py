from django.urls import path

from .views import profile_picture_request

app_name = "photo"

urlpatterns = [
    path("profile_picture/", profile_picture_request, name="profile-picture")
]
