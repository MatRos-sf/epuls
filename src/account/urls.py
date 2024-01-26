from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .views import AboutUserView, ProfileUpdateView, ProfileView, signup

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
                path(
                    "update/profile", ProfileUpdateView.as_view(), name="profile-update"
                ),
                path(
                    "update/aboutuser", AboutUserView.as_view(), name="aboutuser-update"
                ),
            ]
        ),
    ),
]
