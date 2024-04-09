from typing import Any, Optional

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, reverse

from epuls_tools.views import (
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
        instance.author = self.login_user()
        instance.save()
        return super().form_valid(form)

    def test_func(self):
        return self.check_users()


class DiaryDetailView(LoginRequiredMixin, EpulsDetailView):
    template_name = "account/diary/detail.html"
    model = Diary
    activity = ActionType.DIARY

    def get_object(self, queryset=None) -> Any:
        user = self.url_user()
        pk = int(self.kwargs.get("pk"))

        diary_instance = get_object_or_404(Diary, author=user, pk=pk)

        if diary_instance.is_hide and not self.check_users():
            return Diary.objects.none()

        return diary_instance


class DiaryUpdateView(LoginRequiredMixin, UserPassesTestMixin, EpulsUpdateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Update"}
    activity = ActionType.DIARY

    def test_func(self):
        return self.check_users()

    def get_object(self, queryset=None):
        return get_object_or_404(
            Diary,
            author=self.url_user(),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryDeleteView(LoginRequiredMixin, UserPassesTestMixin, EpulsDeleteView):
    model = Diary
    template_name = "account/diary/confirm_delete.html"
    activity = ActionType.DIARY

    def get_success_url(self):
        user = self.login_user()
        return reverse("account:diary", kwargs={"username": user.username})

    def test_func(self):
        return self.check_users()

    def get_object(self, queryset=None):
        return get_object_or_404(
            Diary,
            author=self.url_user(),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryListView(LoginRequiredMixin, EpulsListView):
    template_name = "account/diary/list.html"
    paginate_by = 10
    activity = ActionType.DIARY

    def get_queryset(self):
        user = self.url_user()
        user = get_object_or_404(User, username=user.username)

        if self.check_users():
            return Diary.objects.filter(author=user)

        return Diary.objects.filter(author=user, is_hide=False)

    def get_context_data(self, **kwargs):
        """
        Extra context:
            * owner -> it's username form url
        """
        context = super().get_context_data(**kwargs)
        context["owner"] = self.url_user().username
        return context
