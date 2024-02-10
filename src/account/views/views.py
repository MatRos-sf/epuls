from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import DetailView, ListView, UpdateView

from account.forms import AboutUserForm, GuestbookUserForm, ProfileForm, UserSignupForm
from account.models import AboutUser, Guestbook, Profile, Visitor


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class ProfileView(LoginRequiredMixin, DetailView):
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


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = Profile
    form_class = ProfileForm
    extra_context = {"title": "Update Profile", "action": "Save"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        user = self.get_object()
        return reverse("account:profile", kwargs={"username": user.username})

    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )


class AboutUserView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/forms.html"
    model = AboutUser
    form_class = AboutUserForm
    extra_context = {"title": "About User"}

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        return self.get_object()

    def test_func(self):
        return self.get_object().username == self.request.user.username

    def handle_no_permission(self):
        return JsonResponse(
            {"message": "You do not have permission to update this user."},
            status=HTTPStatus.FORBIDDEN,
        )

    # TODO tutaj będzie sprawdzać czy wszystkie pola są uzupełnione jak nie to wpisuje punkty


class GuestbookView(LoginRequiredMixin, ListView):
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


class FriendsListView(LoginRequiredMixin, ListView):
    template_name = "account/friends.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        return user.profile.friends.all()
