from django import forms

from .models import Gallery, Picture, ProfilePictureRequest


class ProfilePictureRequestForm(forms.ModelForm):
    class Meta:
        model = ProfilePictureRequest
        fields = ("picture",)

    # def __init__(self, *args, **kwargs):
    #     profile = kwargs.pop('profile', None)
    #     super(ProfilePictureRequestForm, self).__init__(*args, **kwargs)
    #
    #     if profile:
    #         self.fields['profile'].queryset = profile


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ("name", "description")


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
