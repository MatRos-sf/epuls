from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from account.models import Profile

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


class ProfilePictureResponseView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "photo/profile_picture_response.html"

    def get_object(self):
        return self.model

    def get(self, request, *args, **kwargs):
        context = {}
        profile_picture = (
            ProfilePictureRequest.objects.filter(is_accepted=False, is_rejected=False)
            .order_by("?")
            .first()
        )
        if profile_picture:
            currently_photo = profile_picture.profile.profile_picture
            if currently_photo:
                context["currently_photo"] = currently_photo.url

        context["object"] = profile_picture

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        picture_id = request.POST.get("profile_picture_id")
        instance = ProfilePictureRequest.objects.get(pk=picture_id)
        getattr(instance, action)()

        return self.get(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_superuser


class GalleryCreateView(LoginRequiredMixin, CreateView):
    form_class = GalleryForm
    template_name = "account/forms.html"
    extra_context = {"topic": "Update Gallery"}

    def form_valid(self, form):
        user_profile = self.request.user.profile
        instance = form.save(commit=False)
        if user_profile.amt_of_galleries < user_profile.pull_field_limit("gallery"):
            instance.profile = self.request.user.profile
            # update Profile.amt_of_galleries + 1
            Profile.objects.filter(id=user_profile.id).update(
                amt_of_galleries=F("amt_of_galleries") + 1
            )
        else:
            messages.error(
                self.request,
                "Gallery cannot be created! Update your profile type to add more galleries. Or delete old ones!",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class GalleryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Gallery
    form_class = GalleryForm
    template_name = "account/forms.html"
    extra_context = {"topic": "Create Gallery"}

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        gallery_pk = self.kwargs.get("pk")
        return get_object_or_404(
            Gallery, profile__user__username=username, pk=gallery_pk
        )

    def test_func(self):
        return self.request.user.username == self.kwargs.get("username")


class GalleryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gallery
    template_name = "photo/gallery/confirm_delete.html"

    def get_success_url(self):
        Profile.objects.filter(user=self.request.user).update(
            amt_of_galleries=F("amt_of_galleries") - 1
        )
        return reverse("photo:gallery", kwargs={"username": self.request.user.username})

    def get_object(self, queryset=None):
        return get_object_or_404(
            Gallery,
            profile__user__username=self.kwargs.get("username"),
            pk=self.kwargs.get("pk"),
        )

    def test_func(self):
        return self.request.user.username == self.kwargs.get("username")


class GalleryDetailView(LoginRequiredMixin, DetailView):
    model = Gallery
    template_name = "photo/gallery/detail.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        gallery_pk = self.kwargs.get("pk")
        return get_object_or_404(
            Gallery, profile__user__username=username, pk=gallery_pk
        )


class GalleryListView(LoginRequiredMixin, ListView):
    model = Gallery
    template_name = "photo/gallery/list.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Gallery.objects.filter(profile__user__username=username)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["self"] = self.kwargs.get("username") == self.request.user.username
        return context


# CRUD PHOTO
class PictureCreateView(LoginRequiredMixin, CreateView):
    model = Picture
    template_name = "photo/picture/form.html"
    form_class = PictureForm

    def get_form_kwargs(self):
        kwargs = super(PictureCreateView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.profile = self.request.user.profile
        return super(PictureCreateView, self).form_valid(form)

    def get_success_url(self):
        instance = self.object
        size = instance.picture.size
        Profile.objects.filter(pk=self.object.profile.pk).update(
            size_of_pictures=F("size_of_pictures") + size
        )
        return super().get_success_url()


class PictureUpdateView(LoginRequiredMixin, UpdateView):
    model = Picture
    template_name = "photo/picture/form.html"
    form_class = PictureForm


class PictureDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Picture
    template_name = "photo/picture/detail.html"

    def test_func(self):
        pk = self.kwargs.get("pk")
        return Picture.objects.filter(
            gallery__profile__user=self.request.user, pk=pk
        ).exists()


class PictureDeleteView(LoginRequiredMixin, DeleteView):
    model = Picture
    template_name = "photo/picture/confirm_delete.html"

    def get_success_url(self):
        return reverse("photo:gallery", kwargs={"username": self.request.user.username})

    def test_func(self):
        pk = self.kwargs.get("pk")
        return Picture.objects.filter(
            gallery__profile__user=self.request.user, pk=pk
        ).exists()
