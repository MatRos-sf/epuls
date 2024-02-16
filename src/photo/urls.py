from django.urls import include, path

from .views import (
    GalleryCreateView,
    GalleryDetailView,
    GalleryListView,
    profile_picture_request,
)

app_name = "photo"

urlpatterns = [
    path("profile_picture/", profile_picture_request, name="profile-picture"),
    path(
        "gallery/",
        include(
            [
                path("create", GalleryCreateView.as_view(), name="gallery-create"),
                path(
                    "<str:username>/",
                    include(
                        [
                            path("", GalleryListView.as_view(), name="gallery"),
                            path(
                                "<int:pk>/",
                                GalleryDetailView.as_view(),
                                name="gallery-detail",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
