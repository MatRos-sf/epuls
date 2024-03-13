import os
from typing import Dict, Optional

from django import template
from django.utils.safestring import mark_safe
from typing_extensions import LiteralString

from account.models import PROFILE_PICTURE_PATH, Profile, ProfileType

register = template.Library()


@register.simple_tag
def get_gender_picture(gender: str, profile_type: str) -> LiteralString | str | bytes:
    return os.path.join("account", "gender", gender, profile_type + ".jpg")
