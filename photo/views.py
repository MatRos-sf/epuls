from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import GalleryForm, PictureForm, ProfilePictureRequestForm
from .models import Gallery, Picture, ProfilePictureRequest


@login_required
def profile_picture_request(request):
    """
    Creates request model to set a profile picture. When user has sent photo and photo hasn't been accepted or rejected
    then user doesn't create request just edit them.
    """
    picture = ProfilePictureRequest.objects.filter(
        profile=request.user.profile, is_accepted=False, is_rejected=False
    ).first()

    form = ProfilePictureRequestForm(instance=picture)

    if request.method == "POST":
        form = ProfilePictureRequestForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.profile = request.user.profile
            instance.save()

            messages.success(
                request, "Your profile picture request has sent successfully."
            )
            return redirect("account:profile", username=request.user.username)

    return render(request, "photo/profile_picture_request_form.html", {"form": form})


class GalleryCreateView(LoginRequiredMixin, CreateView):
    model = Gallery
    form_class = GalleryForm
    template_name = "photo/gallery_form.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.profile = self.request.user.profile
        return super(GalleryCreateView, self).form_valid(instance)


class GalleryDetailView(LoginRequiredMixin, DetailView):
    model = Gallery
    template_name = "photo/gallery_detail.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        gallery_pk = self.kwargs.get("pk")
        return get_object_or_404(
            Gallery, profile__user__username=username, pk=gallery_pk
        )


class GalleryListView(LoginRequiredMixin, ListView):
    model = Gallery
    template_name = "photo/gallery.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Gallery.objects.filter(profile__user__username=username)


# CRUD PHOTO
class PictureCreateView(LoginRequiredMixin, CreateView):
    model = Picture
    template_name = "photo/gallery_form.html"
    form_class = PictureForm

    def get_form_kwargs(self):
        kwargs = super(PictureCreateView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.profile = self.request.user.profile
        return super(PictureCreateView, self).form_valid(form)


class PictureUpdateView(LoginRequiredMixin, UpdateView):
    model = Picture
    template_name = "photo/gallery_form.html"
    form_class = PictureForm


class PictureDetailView(LoginRequiredMixin, DetailView):
    model = Picture
    template_name = "photo/picture/detail.html"


class PictureDeleteView(LoginRequiredMixin, DeleteView):
    model = Picture
    template_name = "photo"


class PictureView(LoginRequiredMixin, ListView):
    model = Picture
    template_name = "photo/picture-list.html"
