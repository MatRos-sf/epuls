from django.urls import path

from .views import PulsDetailView, update_puls

urlpatterns = [
    path("update/", update_puls, name="puls-update"),
    path("", PulsDetailView.as_view(), name="puls"),
]
