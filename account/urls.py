from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import include, path, reverse_lazy

from .views import (
    AboutUserUpdateView,
    AddBestFriendsView,
    BestFriendsListView,
    EpulsLoginView,
    FriendsListView,
    HomeView,
    InvitesListView,
    PresentationUpdateView,
    ProfileUpdateView,
    ProfileView,
    RemoveBestFriendsView,
    SettingsTemplateView,
    UserListView,
    UserNameChangeView,
    activate,
    invite_accept,
    send_to_friends,
    signup,
    unfriend,
)

app_name = "account"

urlpatterns_password_reset = [
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="account/authorisation/password_reset_form.html",
            email_template_name="account/authorisation/password_reset_email.html",
            success_url=reverse_lazy("account:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="account/authorisation/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="account/authorisation/password_reset_confirm.html",
            success_url=reverse_lazy("account:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="account/authorisation/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]

# This urlpatterns including user's settings
urlpatterns_settings = [
    path(
        "settings/",
        include(
            [
                # account
                path("", SettingsTemplateView.as_view(), name="settings"),
                path(
                    "password-change/",
                    PasswordChangeView.as_view(
                        template_name="account/authorisation/password_change_form.html",
                        success_url=reverse_lazy("account:password_change_done"),
                    ),
                    name="password_change",
                ),
                path(
                    "password-change/done/",
                    PasswordChangeDoneView.as_view(),
                    name="password_change_done",
                ),
                path(
                    "username-change/",
                    UserNameChangeView.as_view(),
                    name="username-change",
                ),
                # Profile
                path("profile/", ProfileUpdateView.as_view(), name="update-profile"),
                path("aboutuser/", AboutUserUpdateView.as_view(), name="update-about"),
            ]
        ),
    )
]


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    # authorisation
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("login/", EpulsLoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    # password reset
    *urlpatterns_password_reset,
    # settings account
    *urlpatterns_settings,
    path("signup/", signup, name="signup"),
    path("send_request/<str:username>/", send_to_friends, name="send_invitation"),
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
