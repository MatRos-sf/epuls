from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import AboutUser, Gender, Profile
from .models.emotion import BasicEmotion, DivineEmotion, ProEmotion, XtremeEmotion

FORM_CLASS = "form-group col-md-6 m-0 p-3"


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
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control form-control-sm"},
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Profile
        fields = (
            "date_of_birth",
            "short_description",
            "voivodeship",
            "gender",
            "emotion",
        )

        widgets = {
            "gender": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "emotion": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "voivodeship": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "short_description": forms.TextInput(
                attrs={"class": "form-control form-control-sm"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        emotion_choices = list(BasicEmotion.choices)

        if instance.type_of_profile == "P":
            emotion_choices += list(ProEmotion.choices)
        elif instance.type_of_profile == "X":
            emotion_choices += [*ProEmotion.choices, *XtremeEmotion.choices]
        elif instance.type_of_profile == "D":
            emotion_choices += [
                *ProEmotion.choices,
                *XtremeEmotion.choices,
                *DivineEmotion.choices,
            ]

        self.fields["emotion"].choices = emotion_choices

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("date_of_birth", css_class="form-group col-md-3 m-0 p-3"),
                Column("voivodeship", css_class="form-group col-md-3 m-0 p-3"),
                Column("gender", css_class="form-group col-md-3 m-0 p-3"),
                Column("emotion", css_class="form-group col-md-3 m-0 p-3"),
                css_class="row",
            ),
            Row(
                Column("short_description", css_class="form-group col-md-6 mb-0"),
                css_class="row justify-content-center",
            ),
            Submit("submit", "Update", css_class="btn btn-sm btn-success m-2"),
        )


class AboutUserForm(forms.ModelForm):
    class Meta:
        model = AboutUser
        fields = "__all__"
        exclude = ["is_set"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.label = ""

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-lg"
            visible.field.widget.attrs["placeholder"] = visible.name

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("height", css_class=FORM_CLASS),
                Column("weight", css_class=FORM_CLASS),
                css_class="row",
            ),
            Row(
                Column("politics", css_class=FORM_CLASS),
                Column("idol", css_class=FORM_CLASS),
                css_class="row",
            ),
            Row(
                Column("film", css_class=FORM_CLASS),
                Column("song", css_class=FORM_CLASS),
                css_class="row",
            ),
            Row(
                Column("dish", css_class="form-group col-md-6 mb-0"),
                css_class="row justify-content-center",
            ),
            Submit("submit", "Update", css_class="btn btn-sm btn-success m-2"),
        )


class PresentationForm(forms.ModelForm):
    presentation = forms.CharField(
        widget=forms.Textarea(
            attrs={"class:": "form-control", "rows": "25", "cols": "100"}
        )
    )

    class Meta:
        model = Profile
        fields = ("presentation",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.label = ""
