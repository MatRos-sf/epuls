from django.urls import path

from .views import (
    DiaryCreateView,
    DiaryDeleteView,
    DiaryDetailView,
    DiaryListView,
    DiaryUpdateView,
)

# app_name = "diary"

urlpatterns = [
    path("", DiaryListView.as_view(), name="diary"),
    path("create/", DiaryCreateView.as_view(), name="diary-create"),
    path(
        "<int:pk>/",
        DiaryDetailView.as_view(),
        name="diary-detail",
    ),
    path(
        "<int:pk>/update/",
        DiaryUpdateView.as_view(),
        name="diary-update",
    ),
    path(
        "<int:pk>/delete/",
        DiaryDeleteView.as_view(),
        name="diary-delete",
    ),
]
