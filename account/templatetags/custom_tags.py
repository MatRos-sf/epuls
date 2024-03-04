from typing import Dict, Optional

from django import template

register = template.Library()


@register.simple_tag
def get_username(slags: Dict, default_username: str):
    username = slags.get("username", None)
    return username if username else default_username


@register.simple_tag
def get_about(text: Optional[str] = None) -> str:
    return text if text else str()
