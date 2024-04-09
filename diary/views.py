from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, reverse

from account.views.base import (
    ActionType,
    EpulsCreateView,
    EpulsDeleteView,
    EpulsDetailView,
    EpulsListView,
    EpulsUpdateView,
)

from .forms import DiaryForm
from .models import Diary


class DiaryCreateView(LoginRequiredMixin, UserPassesTestMixin, EpulsCreateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Edit"}
    activity = ActionType.DIARY

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        return super().form_valid(form)

    def test_func(self):
        username = self.kwargs.get("username")
        return self.request.user.username == username


class DiaryDetailView(LoginRequiredMixin, EpulsDetailView):
    template_name = "account/diary/detail.html"
    model = Diary
    activity = ActionType.DIARY

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


class DiaryUpdateView(LoginRequiredMixin, UserPassesTestMixin, EpulsUpdateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Update"}
    activity = ActionType.DIARY

    def test_func(self):
        username = self.kwargs.get("username")
        return self.request.user.username == username

    def get_object(self, queryset=None):
        return get_object_or_404(
            Diary,
            author__username=self.kwargs.get("username"),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryDeleteView(LoginRequiredMixin, UserPassesTestMixin, EpulsDeleteView):
    model = Diary
    template_name = "account/diary/confirm_delete.html"
    activity = ActionType.DIARY

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


class DiaryListView(LoginRequiredMixin, EpulsListView):
    template_name = "account/diary/list.html"
    paginate_by = 10
    activity = ActionType.DIARY

    def __get_user_for_url(self) -> Optional[str]:
        return self.kwargs.get("username", None)

    def get_queryset(self):
        username = self.__get_user_for_url()

        user = get_object_or_404(User, username=username)
        if user == self.request.user:
            return Diary.objects.filter(author=user)
        return Diary.objects.filter(author=user, is_hide=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.__get_user_for_url()
        return context
