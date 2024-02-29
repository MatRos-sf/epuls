from django import forms

# from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import AboutUser, Diary, Gender, Guestbook, Profile


class UserSignupForm(UserCreationForm):
    email = forms.EmailField()
    gender = forms.ChoiceField(choices=Gender)

    class Meta:
        model = User
        fields = ["username", "gender", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    # date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1950, 2025)))
    date_of_birth = forms.DateField(
        label="Date of Birth",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Profile
        fields = ("date_of_birth", "short_description", "voivodeship")


class AboutUserForm(forms.ModelForm):
    class Meta:
        model = AboutUser
        fields = "__all__"


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


class DiaryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["class"] = "form-control mx-4 "
        self.fields["content"].widget.attrs["placeholder"] = (
            "Today is a new day, full of possibilities and experiences. "
            "Write down your thoughts, dreams, and experiences below to "
            "immortalize the moments that made today special."
        )
        self.fields["content"].label = ""

        self.fields["title"].widget.attrs["class"] = "form-control mx-4 my-2"
        self.fields["title"].widget.attrs["placeholder"] = "Title"
        self.fields["title"].label = ""

    class Meta:
        model = Diary
        fields = ["title", "content", "is_hide"]
