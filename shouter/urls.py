from django.urls import path

from .views import ShouterCreateView

app_name = "shouter"

urlpatterns = [path("create/", ShouterCreateView.as_view(), name="create")]
