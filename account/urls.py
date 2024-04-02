from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from puls.views import PulsDetailView, update_puls

from .views import (
    AboutUserUpdateView,
    AddBestFriendsView,
    BestFriendsListView,
    DiaryCreateView,
    DiaryDeleteView,
    DiaryDetailView,
    DiaryListView,
    DiaryUpdateView,
    FriendsListView,
    GuestbookView,
    HomeView,
    InvitesListView,
    ProfileUpdateView,
    ProfileView,
    RemoveBestFriendsView,
    UserListView,
    invite_accept,
    send_to_friends,
    signup,
    unfriend,
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
                path(
                    "best-friends/",
                    include(
                        [
                            path(
                                "", BestFriendsListView.as_view(), name="best-friends"
                            ),
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
                path(
                    "puls/",
                    include(
                        [
                            path("update/", update_puls, name="puls-update"),
                            path("", PulsDetailView.as_view(), name="puls"),
                        ]
                    ),
                ),
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
