import os
from typing import Dict, Optional

from django import template
from django.utils.safestring import mark_safe
from typing_extensions import LiteralString

from account.models import PROFILE_PICTURE_PATH, Profile, ProfileType

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
        html_code = f"<p class='m-1'><b>Swing by your profile:</b> {user_profile.count_visitors}</p>"

    elif user_profile.type_of_profile == ProfileType.DIVINE:
        html_code = (
            f"<p class='m-1'><b>Swing by your profile:</b> {user_profile.count_visitors}</p>"
            f"<p class='m-1'><b>Female:</b> {user_profile.female_visitor}</p>"
            f"<p class='m-1 '><b>Male:</b> {user_profile.male_visitor}</p>"
        )

    return mark_safe(html_code)  # nosec
