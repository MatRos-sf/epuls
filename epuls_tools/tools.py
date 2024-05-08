from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from puls.models import PulsType, SinglePuls

from .scaler import give_away_puls


def puls_valid_time_gap_comments(
    user: User, comment_gap: timedelta, puls_type: PulsType
) -> None:
    """
    Give a points when  time between comments is great than 'comment_gap' minutes.
    """

    time_now = timezone.now()

    is_time_span = SinglePuls.objects.filter(
        puls=user.profile.puls,
        created__gte=time_now - comment_gap,
        type=puls_type,
    ).exists()

    if not is_time_span:
        give_away_puls(
            user_profile=user.profile, type=PulsType.COMMENT_ACTIVITY_PICTURE
        )
