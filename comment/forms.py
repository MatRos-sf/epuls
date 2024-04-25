from django import forms

from .models import PhotoComment


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ("comment",)

        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": "3"})
        }
