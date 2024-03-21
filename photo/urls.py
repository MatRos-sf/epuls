from django.urls import include, path

from .views import (
    GalleryCreateView,
    GalleryDeleteView,
    GalleryDetailView,
    GalleryListView,
    GalleryUpdateView,
    PictureCreateView,
    PictureDeleteView,
    PictureDetailView,
    PictureUpdateView,
    PictureView,
    ProfilePictureResponseView,
    profile_picture_request,
)

app_name = "photo"

urlpatterns = [
    path(
        "profile_picture/",
        include(
            [
                path(
                    "request/", profile_picture_request, name="profile-picture-request"
                ),
                path(
                    "response/",
                    ProfilePictureResponseView.as_view(),
                    name="profile-picture-response",
                ),
            ]
        ),
    ),
    path(
        "gallery/",
        include(
            [
                path("create/", GalleryCreateView.as_view(), name="gallery-create"),
                path(
                    "<str:username>/",
                    include(
                        [
                            path("", GalleryListView.as_view(), name="gallery"),
                            path(
                                "<int:pk>/",
                                include(
                                    [
                                        path(
                                            "",
                                            GalleryDetailView.as_view(),
                                            name="gallery-detail",
                                        ),
                                        path(
                                            "update/",
                                            GalleryUpdateView.as_view(),
                                            name="gallery-update",
                                        ),
                                        path(
                                            "delete/",
                                            GalleryDeleteView.as_view(),
                                            name="gallery-delete",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path("", PictureView.as_view(), name="picture"),
    path("create/", PictureCreateView.as_view(), name="picture-create"),
    path(
        "<int:pk>/",
        include(
            [
                path("", PictureDetailView.as_view(), name="picture-detail"),
                path("delete/", PictureDeleteView.as_view(), name="picture-delete"),
                path("update/", PictureUpdateView.as_view(), name="picture-update"),
            ]
        ),
    ),
]
