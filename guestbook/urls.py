from django.urls import path

from .views import GuestbookView

urlpatterns = [
    path("", GuestbookView.as_view(), name="guestbook"),
]
