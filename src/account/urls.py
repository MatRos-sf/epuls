from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .views import (
    AboutUserView,
    DiaryCreateView,
    DiaryDetailView,
    DiaryUpdateView,
    GuestbookView,
    ProfileUpdateView,
    ProfileView,
    signup,
)

app_name = "account"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="account/login.html"), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="account/logout.html"),
        name="logout",
    ),
    path("signup/", signup, name="signup"),
    path(
        "<str:username>/",
        include(
            [
                path("", ProfileView.as_view(), name="profile"),
                path("gb/", GuestbookView.as_view(), name="guestbook"),
                path(
                    "diary/",
                    include(
                        [
                            path(
                                "create/",
                                DiaryCreateView.as_view(),
                                name="diary-create",
                            ),
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
                        ]
                    ),
                ),
            ]
        ),
    ),
    path(
        "accounts/edit/",
        include(
            [
                path("profile/", ProfileUpdateView.as_view(), name="update-profile"),
                path("aboutuser/", AboutUserView.as_view(), name="update-about"),
            ]
        ),
    ),
]
