from datetime import timedelta
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View
from django.views.generic.edit import FormMixin

from account.models import Profile
from comment.forms import PhotoCommentForm
from comment.models import PhotoComment
from epuls_tools.tools import puls_valid_time_gap_comments
from epuls_tools.views import ActionType, EpulsDetailView, EpulsListView
from puls.models import PulsType

from .forms import GalleryForm, PictureForm, ProfilePictureRequestForm
from .models import Gallery, GalleryStats, Picture, PictureStats, ProfilePictureRequest


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
        try:
            return Gallery.objects.select_related("profile__user").get(
                profile__user__username=username, pk=gallery_pk
            )
        except Gallery.DoesNotExist:
            raise Http404()


class GalleryListView(LoginRequiredMixin, EpulsListView):
    model = Gallery
    template_name = "photo/gallery/list.html"
    activity = ActionType.GALLERY

    def get_queryset(self) -> Any:
        username = self.kwargs.get("username")
        return Gallery.objects.filter(profile__user__username=username)

    def get_context_data(self, *, object_list=None, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["self"] = self.check_users()
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
        instance.profile.save()
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


class PictureDetailView(LoginRequiredMixin, FormMixin, EpulsDetailView):
    """
    A view for displaying detailed information about a picture and with form for adding comment.
    """

    model = Picture
    template_name = "photo/picture/detail.html"
    form_class = PhotoCommentForm
    activity = ActionType.PHOTO

    # it's time between comments gap when user can get points.
    comment_gap = timedelta(minutes=5)

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        return Picture.objects.select_related(
            "gallery", "profile", "profile__user"
        ).get(pk=pk)

    def get_success_url(self) -> str:
        """Return the URL to redirect to after a successful form submission."""
        return self.object.get_absolute_url()

    def form_valid(self, form) -> HttpResponseRedirect:
        """Add necessary fields (photo and author) to create a Comment model."""
        login_user = self.get_login_user()
        object_instance = self.object

        instance = form.save(commit=False)
        instance.photo = object_instance
        instance.author = login_user
        instance.save()

        # give away a puls when user isn't login one
        if not self.check_users():
            puls_valid_time_gap_comments(
                login_user, self.comment_gap, PulsType.COMMENT_ACTIVITY_PICTURE
            )
            self.send_notification(
                "commented your photo", action_object=object_instance
            )

        # update stats
        self.update_stats(
            gallery_pk=object_instance.gallery.pk, picture_pk=object_instance.pk
        )

        return super().form_valid(form)

    def update_stats(self, gallery_pk: int, picture_pk: int) -> None:
        """Increases field 'amt_comment' by 1 on GalleryStats and PictureStats model."""
        GalleryStats.objects.filter(pk=gallery_pk).update(
            amt_comments=F("amt_comments") + 1
        )
        PictureStats.objects.filter(pk=picture_pk).update(
            amt_comments=F("amt_comments") + 1
        )

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect | Any:
        """Handle POST requests."""

        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = PhotoComment.objects.select_related("author", "author__profile")
        context["comments"] = comments.filter(photo=context["object"])
        return context

    # def noti(self, actor: User, recipient: User, verb: str, act_obj: Any, **kwargs):
    #     from notifications.signals import notify
    #
    #     notify.send(
    #         sender=actor, actor=actor, recipient=recipient, verb=verb, action_object=act_obj, **kwargs
    #     )


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
