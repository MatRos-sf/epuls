from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView

from .forms import GalleryForm, ProfilePictureRequestForm
from .models import Gallery


@login_required
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
