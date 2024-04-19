from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from account.forms import UserSignupForm
from account.models import Profile
from epuls_tools.scaler import give_away_puls
from puls.models import PulsType

__all__ = [
    "generate_confirmation_token",
    "send_confirmation_email",
    "signup",
    "activate",
    "EpulsLoginView",
]


def generate_confirmation_token(user) -> str:
    return default_token_generator.make_token(user)


def send_confirmation_email(current_site, user) -> None:
    token = generate_confirmation_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    subject = "Activate your account"
    message = render_to_string(
        "account/authorisation/email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
        },
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, (user.email,))


def signup(
    request,
) -> HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    """
    View responsible for user signup.
    """
    form = UserSignupForm()

    if request.method == "POST":
        form = UserSignupForm(request.POST)

        if form.is_valid():
            gender = form.cleaned_data.pop("gender")
            instance = form.save()
            # set a gender
            profile = instance.profile
            profile.gender = gender
            profile.save()

            # send email
            current_site = get_current_site(request)
            send_confirmation_email(current_site, profile.user)  # TODO celery

            return redirect("account:login")

    return render(
        request, "account/base/basic_form.html", {"form": form, "title": "Sign Up"}
    )


def activate(
    request, uidb64, token
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """
    Confirm the email associated with the user's profile.

    If the provided token is valid, mark the profile as confirmed ('is_confirm' set) and award a point for email confirmation.
    If the token has expired, generate a new token and send it to email user's.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user:
        token_is_active = default_token_generator.check_token(user, token)
        if not user.profile.is_confirm and token_is_active:
            user.profile.is_confirm = True
            user.profile.save(update_fields=["is_confirm"])
            # give puls
            give_away_puls(user_profile=user.profile, type=PulsType.ACCOUNT_CONFIRM)
            messages.success(request, "Your account has been confirmed!")

        elif not user.profile.is_confirm and not token_is_active:
            current_site = get_current_site(request)
            send_confirmation_email(current_site, user)
            messages.warning(
                request,
                "Token has expired. New confirmation link has been sent to your email.",
            )
        else:
            messages.warning(request, "Your email was confirmed!")
    else:
        messages.error(request, "Token is wrong!")

    return redirect("account:login")


class EpulsLoginView(LoginView):
    template_name = "account/login.html"

    def form_valid(self, form):
        """
        When form valid, user's will get points for login
        """
        username = form.cleaned_data.get("username")
        user_profile = Profile.objects.get(user__username=username)
        give_away_puls(user_profile=user_profile, type=PulsType.LOGINS)
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # logout user when is login !
        if request.user.is_authenticated:
            messages.warning(request, "You have been logout!")
            logout(request)

        return super().get(request, *args, **kwargs)
