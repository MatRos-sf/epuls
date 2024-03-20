from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from .models import Gallery, Picture, ProfilePictureRequest


class ProfilePictureRequestForm(forms.ModelForm):
    class Meta:
        model = ProfilePictureRequest
        fields = ("picture",)


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ("name", "description")

    def __init__(self, *args, **kwargs):
        super(GalleryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ""

        for visible in self.visible_fields():
            visible.field.label = ""
            visible.field.widget.attrs["placeholder"] = visible.name

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6 m-0 p-3"),
                css_class="row justify-content-center",
            ),
            Row(
                Column("description", css_class="form-group col-md-8"),
                css_class="row justify-content-center",
            ),
            Submit("submit", "Save", css_class="btn btn-sm btn-success m-3"),
        )


class PictureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(PictureForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["gallery"].queryset = Gallery.objects.filter(
                profile=user.profile
            )

    class Meta:
        model = Picture
        exclude = ("profile", "date_created")
