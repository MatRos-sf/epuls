CONSTANT_PULS = ("profile_photo", "about_me", "presentation", "schools")
CONSTANT_PULS_QTY = 15


def scale_puls(name_type):
    if name_type in CONSTANT_PULS:
        return CONSTANT_PULS_QTY
    raise NotImplementedError
