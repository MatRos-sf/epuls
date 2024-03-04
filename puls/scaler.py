from account.models import Profile, ProfileType

from .models import PulsType, SinglePuls

CONSTANT_PULS = ("profile_photo", "about_me", "presentation", "schools")
CONSTANT_PULS_QTY = 15

EXTRA_PULS_BY_PROFILE_TYPE = {
    ProfileType.BASIC: 1,
    ProfileType.PRO: 2,
    ProfileType.XTREME: 3,
    ProfileType.DIVINE: 4,
}

PULS_FOR_ACTION = {PulsType.GUESTBOOKS: 0.1}


def scale_puls(name_type):
    if name_type in CONSTANT_PULS:
        return CONSTANT_PULS_QTY
    raise NotImplementedError


# def give_a_puls(func):
#     def wrapper(*args, **kwargs):
#         # Filter
#         f = func(*args, **kwargs)


def add_guestbook_puls(user_profile: Profile, type: PulsType) -> float:
    """
    Generates SinglePuls for entry.
    | Basic |  Pro  | Xtreme | Divine|
    |  0.1  |  0.2  |  0.3   | 0.4  |
    """
    quantity = (
        PULS_FOR_ACTION[type] * EXTRA_PULS_BY_PROFILE_TYPE[user_profile.type_of_profile]
    )
    SinglePuls.objects.create(quantity=quantity, puls=user_profile.puls, type=type)
    return quantity
