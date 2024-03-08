import os
from typing import Dict, Optional

from django import template
from django.conf import settings
from typing_extensions import LiteralString

from account.models import PROFILE_PICTURE_PATH

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
