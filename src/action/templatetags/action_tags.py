from random import choice

from django import template
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

register = template.Library()

MESSAGE_OWN_PROFILE = ("He is checking his reflection!", "He is browsing his profile!")


@register.simple_tag
def action_tag(action=None):
    base = "<b>Action: </b>"
    if not action:
        return format_html(base + "Hello everybody. I'm new here ;)")

    lag = (timezone.now() - action.date).seconds
    if lag <= 600:  # 10 min
        if action.action.startswith("own_"):
            return format_html(base + choice(MESSAGE_OWN_PROFILE))
        else:
            href = reverse("account:profile", kwargs={"username": action.whom.username})
            return format_html(
                base
                + f"Spies on <a class='link-secondary link-underline-opacity-0 ' href='{href}'> {action.whom.username} </a>."
            )
    elif 600 < lag <= 900:  # 10 - 15
        return format_html("<b>BRB</b>")
    elif 900 < lag <= 86400:  # 15 min - 1 day
        return format_html("<b>Offline</b>")
    elif 86400 < lag <= 2592000:  # 1 day - 30 days
        return format_html("<b>Ślad po niej zaginął<b>")
    else:
        return format_html("absence of the pulse")
