from django.db import models


class Puls(models.Model):
    profile_photo = models.FloatField(
        default=0, help_text="PLUS for accepted profile photo."
    )
    about_me = models.FloatField(
        default=0, help_text="PLUS for fill the section 'about me' in."
    )
    presentation = models.FloatField(
        default=0, help_text="PLUS for fill own presentation in."
    )
    schools = models.FloatField(default=0, help_text="PLUS for fill schools in.")

    logins = models.FloatField(default=0, help_text="PLUS for log in to the server.")
    guestbooks = models.FloatField(
        default=0, help_text="PLUS for entres to guestbooks."
    )
    diaries = models.FloatField(default=0, help_text="PLUS for entres to diaries.")
    surfing = models.FloatField(default=0, help_text="PLUS for surfint the Epuls.")
    activity = models.FloatField(
        default=0, help_text="PLUS for other different activities."
    )
    type = models.FloatField(
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
        constant_value = sum([p for p in self.constant_value().values()])
        variable_value = sum([p for p in self.variable_value().values()])
        return int(sum([constant_value, variable_value]))
