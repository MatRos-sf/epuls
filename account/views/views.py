from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from account.forms import UserSignupForm


class HomeView(View):
    # TODO: login here
    def get(self, request):
        recently_login_users = User.objects.all().order_by("-last_login")[:5]

        # TODO: recently_login_women, recently_login_man, rag 3
        new_users = User.objects.all().order_by("-date_joined")[:5]

        context = {"recently_login_users": recently_login_users, "new_users": new_users}

        return render(request, "account/home.html", context)


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            gender = form.cleaned_data.pop("gender")
            instance = form.save()
            # set a gender
            profile = instance.profile
            profile.gender = gender
            profile.save()

            return redirect("account:login")

    return render(request, "account/forms.html", {"form": form, "title": "Sign Up"})


class UserListView(ListView):
    model = User
    template_name = "account/user_list.html"

    def get_queryset(self):
        q = self.request.GET.get("q", None)
        if q:
            return User.objects.filter(username__icontains=q)
        return User.objects.all()
