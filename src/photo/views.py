from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProfilePictureRequestForm


def profile_picture_request(request):
    form = ProfilePictureRequestForm()
    if request.method == "POST":
        form = ProfilePictureRequestForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.profile = request.user.profile
            instance.save()
            messages.success(
                request, "Your profile picture request has sent successfully."
            )
            return redirect("profile", username=request.user.username)

    return render(request, "photo/profile_picture_request_form.html", {"form": form})
