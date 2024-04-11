import os
import re
from functools import partial
from typing import Dict, List, Optional, Tuple

from django import template
from django.shortcuts import reverse
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from typing_extensions import LiteralString

from account.models import PROFILE_PICTURE_PATH, Profile, ProfileType
from epuls_tools.presentation import Presentation

register = template.Library()


@register.simple_tag
def get_username(slags: Dict, default_username: str):
    username = slags.get("username", None)
    return username if username else default_username


@register.simple_tag
def get_about(text: Optional[str] = None) -> str:
    return text if text else str()


@register.simple_tag
def get_default_picture_photo(gender: str) -> LiteralString | str | bytes:
    return os.path.join(
        "account", PROFILE_PICTURE_PATH, f"default_{gender}_picture.jpeg"
    )


@register.simple_tag
def get_information_about_visitor(user_profile: Profile):
    html_code = ""
    if user_profile.type_of_profile == ProfileType.XTREME:
        html_code = f"<p class='mt-2'><b>Swing by your profile:</b> {user_profile.count_visitors}</p>"

    elif user_profile.type_of_profile == ProfileType.DIVINE:
        html_code = (
            f"<p class='mt-2 mb-0'><b>Swing by your profile:</b> {user_profile.count_visitors}</p>"
            f"<p class='my-0'><b>Female:</b> {user_profile.female_visitor}</p>"
            f"<p class='my-0 '><b>Male:</b> {user_profile.male_visitor}</p>"
        )

    return mark_safe(html_code)  # nosec


def find_username(html):
    matches = re.finditer(r"<a href=@(\w+).*></a>", html)
    for match in matches:
        print(match.groups()[0])
        print(match.group())


@register.filter(is_safe=True)
def myfilter(value):
    html = Presentation(value)
    a = html.convert()

    return mark_safe(a)  # nosec
