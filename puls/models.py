from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum


class PulsTypeVariableValue(models.TextChoices):
    LOGINS = "logins", "LOGINS"
    GUESTBOOKS = "guestbooks", "GUESTBOOKS"
    MESSAGES = "messages", "MESSAGES"
    DIARIES = "diaries", "DIARIES"
    SURFING = "surfing", "SURFING"
    ACTIVITY = "activity", "ACTIVITY"
    TYPE = "type", "TYPE"


class PulsType(models.TextChoices):
    PROFILE_PHOTO = "profile_photo", "PROFILE PHOTO"
    ABOUT_ME = "about_me", "ABOUT ME"
    PRESENTATION = "presentation", "PRESENTATION"
    SCHOOLS = "schools", "SCHOOLS"
    LOGINS = "logins", "LOGINS"
    GUESTBOOKS = "guestbooks", "GUESTBOOKS"
    MESSAGES = "messages", "MESSAGES"
    DIARIES = "diaries", "DIARIES"
    SURFING = "surfing", "SURFING"
    ACTIVITY = "activity", "ACTIVITY"
    TYPE = "type", "TYPE"
    BONUS = "bonus", "BONUS"


class Puls(models.Model):
    profile_photo = models.IntegerField(
        default=0,
        help_text="PLUS for accepted profile photo.",
        validators=[MinValueValidator(0), MaxValueValidator(15)],
    )
    about_me = models.IntegerField(
        default=0,
        help_text="PLUS for fill the section 'about me' in.",
        validators=[MinValueValidator(0), MaxValueValidator(15)],
    )
    presentation = models.IntegerField(
        default=0,
        help_text="PLUS for fill own presentation in.",
        validators=[MinValueValidator(0), MaxValueValidator(15)],
    )
    schools = models.IntegerField(
        default=0,
        help_text="PLUS for fill schools in.",
        validators=[MinValueValidator(0), MaxValueValidator(15)],
    )

    logins = models.IntegerField(default=0, help_text="PLUS for log in to the server.")
    guestbooks = models.IntegerField(
        default=0, help_text="PLUS for entres to guestbooks."
    )
    messages = models.IntegerField(default=0, help_text="PULS for amount messages.")
    diaries = models.IntegerField(default=0, help_text="PLUS for entres to diaries.")
    surfing = models.IntegerField(default=0, help_text="PLUS for surfint the Epuls.")
    activity = models.IntegerField(
        default=0, help_text="PLUS for other different activities."
    )
    type = models.IntegerField(
        default=0,
        help_text="PLUS for type of account: Pro/Extrime/Divine. Once a month.",
    )

    def constant_value(self) -> dict:
        """
        Returns dictionary with fields that the Puls is constant.
        """
        return {
            "profile_photo": self.profile_photo,
            "about_me": self.about_me,
            "presentation": self.presentation,
            "schools": self.schools,
        }

    @property
    def sum_constant_value(self) -> int:
        return int(sum([p for p in self.constant_value().values()]))

    @property
    def sum_variable_value(self):
        return int(sum([p for p in self.variable_value().values()]))

    def variable_value(self) -> dict:
        """
        Returns dictionary with fields that the Puls is variable.
        """
        return {
            "logins": self.logins,
            "guestbooks": self.guestbooks,
            "diaries": self.diaries,
            "surfing": self.surfing,
            "activity": self.activity,
            "type": self.type,
        }

    def puls(self) -> int:
        """
        Returns sum of Puls. I mean all fields and round it to integer
        :return:
        """
        constant_value = self.sum_constant_value
        variable_value = self.sum_variable_value
        return int(sum([constant_value, variable_value]))

    def check_is_value_set(self, model_attr) -> bool:
        """
        Checks that attr is set or attr is waiting for accepted in SinglePuls.
        """
        value = getattr(self, model_attr)
        is_pulses = SinglePuls.objects.filter(
            puls=self, type=getattr(PulsType, model_attr.upper()), is_accepted=False
        ).exists()

        return value or is_pulses

    def pull_not_accepted_puls(self):
        pulses = self.pulses.filter(is_accepted=False).aggregate(
            profile_photo=Sum(
                "quantity", default=0, filter=Q(type=PulsType.PROFILE_PHOTO)
            ),
            about_me=Sum("quantity", default=0, filter=Q(type=PulsType.ABOUT_ME)),
            presentation=Sum(
                "quantity", default=0, filter=Q(type=PulsType.PRESENTATION)
            ),
            schools=Sum("quantity", default=0, filter=Q(type=PulsType.SCHOOLS)),
            logins=Sum("quantity", default=0, filter=Q(type=PulsType.LOGINS)),
            guestbooks=Sum("quantity", default=0, filter=Q(type=PulsType.GUESTBOOKS)),
            messages=Sum("quantity", default=0, filter=Q(type=PulsType.MESSAGES)),
            diaries=Sum("quantity", default=0, filter=Q(type=PulsType.DIARIES)),
            surfing=Sum("quantity", default=0, filter=Q(type=PulsType.SURFING)),
            activity=Sum("quantity", default=0, filter=Q(type=PulsType.ACTIVITY)),
            type=Sum("quantity", default=0, filter=Q(type=PulsType.TYPE)),
        )
        return pulses


class SinglePuls(models.Model):
    is_accepted = models.BooleanField(default=False)
    quantity = models.FloatField(default=0)
    puls = models.ForeignKey(Puls, on_delete=models.CASCADE, related_name="pulses")
    type = models.CharField(choices=PulsType.choices, max_length=25)

    created = models.DateTimeField(auto_now_add=True)


class Bonus(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    start = models.DateField()
    end = models.DateField()
    scaler = models.FloatField()
    type = models.CharField(
        max_length=50,
        choices=[("all", "ALL"), *PulsTypeVariableValue.choices],
        default="all",
    )

    class Meta:
        verbose_name_plural = "Bonuses"

    def __str__(self):
        return f"{self.name}"
