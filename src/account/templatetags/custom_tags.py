from typing import Dict

from django import template

register = template.Library()


@register.simple_tag
def get_username(slags: Dict, default_username: str):
    username = slags.get("username", None)
    return username if username else default_username
