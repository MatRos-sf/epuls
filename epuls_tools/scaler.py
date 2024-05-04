from functools import wraps

from django.db.models import Q, Sum
from django.utils import timezone

from account.models import Profile, ProfileType
from puls.models import Bonus, PulsType, SinglePuls

CONSTANT_PULS = (
    "profile_photo",
    "about_me",
    "presentation",
    "schools",
    "account_confirm",
)
CONSTANT_PULS_QTY = 15

EXTRA_PULS_BY_PROFILE_TYPE = {
    ProfileType.BASIC: 1,
    ProfileType.PRO: 2,
    ProfileType.XTREME: 3,
    ProfileType.DIVINE: 4,
}

PULS_FOR_ACTION = {
    PulsType.GUESTBOOKS: 0.1,
    PulsType.LOGINS: 0.1,
    PulsType.SURFING: 0.5,
    PulsType.COMMENT_ACTIVITY: 0.2,
}


def give_away_bonus(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Search bonuses if bonuses exist user get extra points for action.
        """

        puls_for_action = func(*args, **kwargs)

        # find all active bonus:
        puls_type = kwargs.get("type")

        if puls_type in CONSTANT_PULS:
            return puls_for_action

        bonus = Bonus.objects.aggregate(
            bonus_sum=Sum(
                "scaler",
                filter=Q(
                    start__lte=timezone.now().date(),
                    end__gte=timezone.now().date(),
                    type__in=["all", puls_type],
                ),
                default=0,
            )
        ).get("bonus_sum")

        quantity = puls_for_action * bonus
        if quantity:
            user_profile = kwargs.get("user_profile")
            SinglePuls.objects.create(
                quantity=quantity, puls=user_profile.puls, type=PulsType.BONUS
            )

        return puls_for_action

    return wrapper


@give_away_bonus
def give_away_puls(
    *, user_profile: Profile, type: PulsType, extra_points: int = 1
) -> float:
    """
    extra_points -> when user pay for activity, user will get extra point
    """
    if type not in CONSTANT_PULS:
        quantity = (
            PULS_FOR_ACTION[type]
            * EXTRA_PULS_BY_PROFILE_TYPE[user_profile.type_of_profile]
            * extra_points
        )
    else:
        quantity = CONSTANT_PULS_QTY

    SinglePuls.objects.create(quantity=quantity, puls=user_profile.puls, type=type)
    return quantity
