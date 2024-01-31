from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import (
    AboutUserForm,
    DiaryForm,
    GuestbookUserForm,
    ProfileForm,
    UserSignupForm,
)
from .models import AboutUser, Diary, Guestbook, Profile, Visitor


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class ProfileView(DetailView):
    model = Profile
    template_name = "account/profile.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        user_instance = get_object_or_404(User, username=username)
        if user_instance != self.request.user.username:
            # user is Visitor
            Visitor.objects.create(visitor=self.request.user, receiver=user_instance)
        return user_instance


class UserSettings(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )


class ProfileUpdateView(UserSettings, UpdateView):
    template_name = "account/forms.html"
    model = Profile
    form_class = ProfileForm
    extra_context = {"title": "Update Profile", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        user = self.get_object()
        return reverse("account:profile", kwargs={"username": user.username})


class AboutUserView(UserSettings, UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        return self.get_object()

    # TODO tutaj będzie sprawdzać czy wszystkie pola są uzupełnione jak nie to wpisuje punkty


class GuestbookView(ListView):
    template_name = "account/guestbook.html"
    model = Guestbook
    extra_context = {"form": GuestbookUserForm}

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Guestbook.objects.filter(receiver__username=username)

    def post(self, request, *args, **kwargs):
        form = GuestbookUserForm(request.POST)
        if form.is_valid():
            username = self.kwargs.get("username")
            instance = form.save(commit=False)
            instance.sender = self.request.user
            instance.receiver = User.objects.get(username=username)
            instance.save()

        return self.get(request, *args, **kwargs)


# CRUD
class DiaryListView(ListView):
    template_name = "account/diary/list.html"

    def get_queryset(self):
        return Diary.objects.filter(author=self.request.user)


class DiaryCreateView(CreateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Edit"}

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        return super().form_valid(form)


class DiaryDetailView(DetailView):
    template_name = "account/diary/detail.html"
    model = Diary


class DiaryUpdateView(UpdateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Update"}


class DiaryDeleteView(DeleteView):
    model = Diary
    template_name = "account/diary/confirm_delete.html"

    def get_success_url(self):
        username = self.request.user.username
        return reverse("account:diary", kwargs={"username": username})
