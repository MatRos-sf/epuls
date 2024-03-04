from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from puls.views import PulsDetailView

from .views import (
    AboutUserUpdateView,
    DiaryCreateView,
    DiaryDeleteView,
    DiaryDetailView,
    DiaryListView,
    DiaryUpdateView,
    FriendsListView,
    GuestbookView,
    HomeView,
    ProfileUpdateView,
    ProfileView,
    signup,
)

app_name = "account"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(template_name="account/login.html"), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="account/logout.html"),
        name="logout",
    ),
    path("signup/", signup, name="signup"),
    path(
        "accounts/edit/",
        include(
            [
                path("profile/", ProfileUpdateView.as_view(), name="update-profile"),
                path("aboutuser/", AboutUserUpdateView.as_view(), name="update-about"),
            ]
        ),
    ),
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
                            path("", DiaryListView.as_view(), name="diary"),
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
                            path(
                                "<int:pk>/delete/",
                                DiaryDeleteView.as_view(),
                                name="diary-delete",
                            ),
                        ]
                    ),
                ),
                path("friends/", FriendsListView.as_view(), name="friends"),
                path("puls/", PulsDetailView.as_view(), name="puls"),
            ]
        ),
    ),
]