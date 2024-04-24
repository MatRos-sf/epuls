from django import forms

TIME_CHOICE = ((1, "An Hour"), (5, "Five Hours"), (24, "One Day"))


class ShouterForm(forms.Form):
    shouter = forms.CharField(max_length=200)
    time = forms.ChoiceField(
        choices=TIME_CHOICE, help_text="How long the shouter should be available."
    )
