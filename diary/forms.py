from django import forms

from .models import Diary


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
