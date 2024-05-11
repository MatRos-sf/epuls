from django import forms

from .models import DiaryComment, PhotoComment


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ("comment",)

        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": "3"})
        }


class DiaryCommentForm(forms.ModelForm):
    class Meta:
        model = DiaryComment
        fields = ("comment",)

        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": "3"})
        }
