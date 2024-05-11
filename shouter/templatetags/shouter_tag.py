from typing import Any

from django import template
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from shouter.models import Shouter

register = template.Library()


def get_user_profile_url(username: str) -> str:
    """
    Generate URL for user profile page.
    """
    return reverse("account:profile", kwargs={"username": username})


def make_user_tag(user: User) -> str:
    """
    Generate HTML tag for user with link to their profile.
    """
    username = user.username
    url = get_user_profile_url(username)

    return f'<a href="{url}" class="fs-5 fw-bold link-offset-2 link-underline link-underline-opacity-0 link-secondary">{username}</a>'


def get_shouter_queryset() -> QuerySet:
    """Get queryset for Shouter object"""
    return Shouter.objects.select_related("user").order_by("?")[:10]


@register.simple_tag(takes_context=True)
def shouter(context) -> Any:
    """Display a list of random shouters."""

    request = context["request"]
    cache_key = f"cached_informations_{request.session.session_key}"
    cached_information = cache.get(cache_key)

    if cached_information:
        return mark_safe(cached_information)  # nosec

    qs = get_shouter_queryset()
    text_list = [
        f'{make_user_tag(s.user)} : <span class="text-dark">{strip_tags(s.text)}</span>'
        for s in qs
    ]
    space = "&nbsp;" * 10

    informations = f"{space}".join(text_list)

    if request.user.is_authenticated:
        cache.set(cache_key, informations, 60 * 5)

    return mark_safe(informations)  # nosec
