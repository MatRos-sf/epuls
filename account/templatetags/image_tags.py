import os

from django import template
from typing_extensions import LiteralString

register = template.Library()


@register.simple_tag
def get_gender_picture(gender: str, profile_type: str) -> LiteralString | str | bytes:
    return os.path.join("account", "gender", gender, profile_type + ".jpg")
