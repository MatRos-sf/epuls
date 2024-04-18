from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.generic import ListView, View


class HomeView(View):
    # TODO: login here
    def get(self, request):
        recently_login_users = User.objects.all().order_by("-last_login")[:5]

        # TODO: recently_login_women, recently_login_man, rag 3
        new_users = User.objects.all().order_by("-date_joined")[:5]

        context = {"recently_login_users": recently_login_users, "new_users": new_users}

        return render(request, "account/home.html", context)


class UserListView(ListView):
    model = User
    template_name = "account/user_list.html"

    def get_queryset(self):
        q = self.request.GET.get("q", None)
        if q:
            return User.objects.filter(username__icontains=q)
        return User.objects.all()
