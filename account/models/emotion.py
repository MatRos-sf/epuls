from django.db import models


class BasicEmotion(models.TextChoices):
    HAPPINESS = "1F601", "Happiness"
    JOY = "1F602", "Joy"
    DELIGHT = "1F603", "Delight"
    SMILE = "1F604", "Smile"
    CONTENTMENT = "1F973", "Contentment"
    AMUSEMENT = "1F639", "Amusement"
    BLISS = "1F607", "Bliss"
    PLAYFULNESS = "1F608", "Playfulness"
    WINK = "1F609", "Wink"
    PLEASURE = "1F60A", "Pleasure"
    SATISFACTION = "1F60B", "Satisfaction"
    RELIEF = "1F60C", "Relief"
    ADORATION = "1F60D", "Adoration"
    COOLNESS = "1F60E", "Coolness"
    SMIRK = "1F60F", "Smirk"


class ProEmotion(models.TextChoices):
    NEUTRALITY = "1F610", "Neutrality"
    INDIFFERENCE = "1F611", "Indifference"
    DISPLEASURE = "1F612", "Displeasure"
    ANNOYANCE = "1F613", "Annoyance"
    PENSIVENESS = "1F614", "Pensiveness"


class XtremeEmotion(models.TextChoices):
    CONFUSION = "1F615", "Confusion"
    DISCONCERT = "1F616", "Disconcert"
    KISSING = "1F618", "Kissing"
    TENDERNESS = "1F619", "Tenderness"
    ROMANCE = "1F61A", "Romance"
    PLAYFUL_TEASE = "1F61B", "Playful Tease"
    CHEEKY = "1F61C", "Cheeky"
    SAUCY = "1F61D", "Saucy"
    DISAPPOINTMENT = "1F61E", "Disappointment"
    WORRY = "1F61F", "Worry"
    ANGER = "1F620", "Anger"
    FRUSTRATION = "1F621", "Frustration"
    SADNESS = "1F622", "Sadness"
    DETERMINATION = "1F623", "Determination"
    TRIUMPH = "1F624", "Triumph"
    MIXED_FEELINGS = "1F625", "Mixed Feelings"
    FRUSTRATED_FROWN = "1F626", "Frustrated Frown"
    DISTRESS = "1F627", "Distress"
    FEAR = "1F628", "Fear"


class DivineEmotion(models.TextChoices):
    WEARINESS = "1F629", "Weariness"
    SLEEPINESS = "1F62A", "Sleepiness"
    TIREDNESS = "1F62B", "Tiredness"
    GRIMACE = "1F62C", "Grimace"
    SOBBING = "1F62D", "Sobbing"
    SURPRISE = "1F632", "Surprise"
    EMBARRASSMENT = "1F633", "Embarrassment"
    NAUSEA = "1F922", "Nausea"
    ANGER_WITH_SWEARING = "1F921", "Anger with Swearing"
    GRATITUDE = "1F64F", "Gratitude"
    OPTIMISM = "1F64C", "Optimism"
    COMPASSION = "1F499", "Compassion"
    PRIDE = "1F4AA", "Pride"
    AFFECTION = "1F48B", "Affection"
    HOPE = "1F4AC", "Hope"
    GRATIFICATION = "1F604", "Gratification"
    ECSTASY = "1F606", "Ecstasy"
    SERENITY = "1F63D", "Serenity"
    EMPATHY = "1F970", "Empathy"
    ACCEPTANCE = "1F64B", "Acceptance"
