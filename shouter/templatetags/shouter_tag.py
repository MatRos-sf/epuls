from django import template
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from faker import Faker

from shouter.models import Shouter

register = template.Library()


def make_user_tag(user: User) -> str:
    username = user.username
    url = reverse("account:profile", kwargs={"username": username})

    return '<a href="{url}">{username}</a>'.format(url=url, username=username)


@register.simple_tag(takes_context=True)
def shouter(context):
    request = context["request"]

    if not request.user.is_authenticated:
        qs = Shouter.objects.order_by("?")[:10]

    else:
        cache_key = f"cached_informations_{request.session.session_key}"
        cached_information = cache.get(cache_key, None)

        if cached_information:
            return cached_information

        qs = Shouter.objects.order_by("?")[:10]

    text_list = []
    for s in qs:
        tag_user = make_user_tag(s.user)
        text_list.append(tag_user + " : " + strip_tags(s.text))

    informations = "   ".join(text_list)

    cache.set(cache_key, informations, 60 * 5)

    return informations
