from django.db import models


class BasicEmotion(models.TextChoices):
    HAPPINESS = "128522", "Happiness"
    SADNESS = "128546", "Sadness"


class ProEmotion(models.TextChoices):
    JEALOUSY = "129336", "JEALOUSY"
    ENVY = "128554", "ENVY"


class XtremeEmotion(models.TextChoices):
    EMPATHY = "128558", "EMPATHY"
    SYMPATHY = "128533", "SYMPATHY"


class DivineEmotion(models.TextChoices):
    GRIEF = "128557", "GRIEF"
    BLISS = "128519", "BLISS"
