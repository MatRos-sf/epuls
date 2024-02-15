from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from account.forms import DiaryForm
from account.models import Diary


class DiaryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Edit"}

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        return super().form_valid(form)

    def test_func(self):
        username = self.kwargs.get("username")
        return self.request.user.username == username


class DiaryDetailView(LoginRequiredMixin, DetailView):
    template_name = "account/diary/detail.html"
    model = Diary

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        pk = int(self.kwargs.get("pk"))

        if username == self.request.user.username:
            return Diary.objects.get(author__username=username, pk=pk)
        else:
            instance = Diary.objects.get(author__username=username, pk=pk)
            if instance.is_hide:
                return None
            return instance


class DiaryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Update"}

    def test_func(self):
        username = self.kwargs.get("username")
        return self.request.user.username == username

    def get_object(self, queryset=None):
        return get_object_or_404(
            Diary,
            author__username=self.kwargs.get("username"),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Diary
    template_name = "account/diary/confirm_delete.html"

    def get_success_url(self):
        username = self.request.user.username
        return reverse("account:diary", kwargs={"username": username})

    def test_func(self):
        username = self.kwargs.get("username")
        return self.request.user.username == username

    def get_object(self, queryset=None):
        return get_object_or_404(
            Diary,
            author__username=self.kwargs.get("username"),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryListView(LoginRequiredMixin, ListView):
    template_name = "account/diary/list.html"

    def get_queryset(self):
        username = self.kwargs.get("username")
        self.kwargs["username"] = username
        user = get_object_or_404(User, username=username)
        if user == self.request.user:
            return Diary.objects.filter(author=user)
        return Diary.objects.filter(author=user, is_hide=False)
