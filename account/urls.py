from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .views import (
    AboutUserUpdateView,
    AddBestFriendsView,
    BestFriendsListView,
    FriendsListView,
    HomeView,
    InvitesListView,
    PresentationUpdateView,
    ProfileUpdateView,
    ProfileView,
    RemoveBestFriendsView,
    UserListView,
    activate,
    invite_accept,
    send_to_friends,
    signup,
    unfriend,
)

app_name = "account"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("login/", LoginView.as_view(template_name="account/login.html"), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="account/logout.html"),
        name="logout",
    ),
    path("signup/", signup, name="signup"),
    path("send_request/<str:username>/", send_to_friends, name="send_invitation"),
    path(
        "accounts/edit/",
        include(
            [
                path("profile/", ProfileUpdateView.as_view(), name="update-profile"),
                path("aboutuser/", AboutUserUpdateView.as_view(), name="update-about"),
            ]
        ),
    ),
    path("users/", UserListView.as_view(), name="user-list"),
    path("unfriend/<str:username>/", unfriend, name="unfriend"),
    path(
        "best-friends/",
        include(
            [
                path("", BestFriendsListView.as_view(), name="best-friends"),
                path(
                    "remove/<int:pk>/",
                    RemoveBestFriendsView.as_view(),
                    name="best-friend-remove",
                ),
                path(
                    "add/<int:pk>/",
                    AddBestFriendsView.as_view(),
                    name="best-friend-add",
                ),
            ]
        ),
    ),
    path("presentation/", PresentationUpdateView.as_view(), name="presentation"),
    path(
        "<str:username>/",
        include(
            [
                path("", ProfileView.as_view(), name="profile"),
                path("gb/", include("guestbook.urls")),
                path("diary/", include("diary.urls")),
                path("friends/", FriendsListView.as_view(), name="friends"),
                path("puls/", include("puls.urls")),
                path(
                    "invites/",
                    include(
                        [
                            path("", InvitesListView.as_view(), name="invites"),
                            path(
                                "accept/<int:pk>/", invite_accept, name="invite-accept"
                            ),
                            path(
                                "reject/<int:pk>/", invite_accept, name="invite-reject"
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
