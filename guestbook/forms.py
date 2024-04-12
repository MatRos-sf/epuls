from django import forms

from .models import Guestbook


class GuestbookUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GuestbookUserForm, self).__init__(*args, **kwargs)
        self.fields["entry"].help_text = None
        self.fields["entry"].label = ""

    class Meta:
        model = Guestbook
        fields = ["entry"]
        widgets = {
            "entry": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Leave a entry here.",
                }
            )
        }

    def clean(self) -> dict:
        cd = self.cleaned_data
        # sender = cd['sender']
        # receiver = cd['receiver']
        #
        # if Guestbook.objects.filter(sender=sender, receiver=receiver).exists():
        #     raise forms.ValidationError("You already have had an entry for this user!")

        return cd
