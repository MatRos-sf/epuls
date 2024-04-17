from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from account.forms import UserSignupForm

__all__ = ["generate_confirmation_token", "send_confirmation_email", "signup"]


def generate_confirmation_token(user):
    return default_token_generator.make_token(user)


def send_confirmation_email(current_site, user) -> None:
    token = generate_confirmation_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    subject = "Activate your account"
    message = render_to_string(
        "account/email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
        },
    )

    send_mail(subject, message, settings.EMAIL_HOST_USER, (user.email,))


def signup(request) -> HttpResponse:
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
