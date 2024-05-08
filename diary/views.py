from datetime import timedelta
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.views.generic.edit import FormMixin

from comment.forms import DiaryCommentForm
from comment.models import DiaryComment
from epuls_tools.mixins import UsernameMatchesMixin
from epuls_tools.tools import puls_valid_time_gap_comments
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


class DiaryCreateView(LoginRequiredMixin, UsernameMatchesMixin, EpulsCreateView):
    template_name = "account/diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Edit"}
    activity = ActionType.DIARY

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.get_login_user()
        instance.save()
        return super().form_valid(form)


class DiaryDetailView(LoginRequiredMixin, FormMixin, EpulsDetailView):
    template_name = "diary/detail.html"
    model = Diary
    form_class = DiaryCommentForm
    activity = ActionType.DIARY
    comment_gap = timedelta(minutes=5)

    def get_object(self, queryset=None) -> Diary:
        user = self.get_user()
        pk = int(self.kwargs.get("pk"))

        try:
            diary_instance = Diary.objects.select_related("author__profile").get(
                author=user, pk=pk
            )
        except Diary.DoesNotExist:
            raise Http404("No Diary matches the given query.")

        if diary_instance.is_hide and not self.check_users():
            raise PermissionDenied()

        return diary_instance

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # pull comments
        comments = DiaryComment.objects.select_related("author", "author__profile")
        context["comments"] = comments.filter(diary=context["object"])

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form: Any) -> HttpResponseRedirect:
        """Extend form valid and add author and diary instance to the form"""
        login_user = self.get_login_user()
        object_instance = self.object

        instance = form.save(commit=False)
        instance.diary = object_instance
        instance.author = login_user
        instance.save()

        if not self.check_users():
            puls_valid_time_gap_comments(login_user, self.comment_gap)

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class DiaryUpdateView(LoginRequiredMixin, UsernameMatchesMixin, EpulsUpdateView):
    template_name = "diary/create.html"
    model = Diary
    form_class = DiaryForm
    extra_context = {"action": "Update"}
    activity = ActionType.DIARY

    def get_object(self, queryset=None) -> Any:
        return get_object_or_404(
            Diary,
            author=self.get_user(),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryDeleteView(LoginRequiredMixin, UsernameMatchesMixin, EpulsDeleteView):
    model = Diary
    template_name = "diary/confirm_delete.html"
    activity = ActionType.DIARY

    def get_success_url(self):
        user = self.get_login_user()
        return reverse("account:diary", kwargs={"username": user.username})

    def get_object(self, queryset=None) -> Any:
        return get_object_or_404(
            Diary,
            author=self.get_user(),
            pk=int(self.kwargs.get("pk")),
        )


class DiaryListView(LoginRequiredMixin, EpulsListView):
    template_name = "diary/list.html"
    paginate_by = 10
    activity = ActionType.DIARY

    def get_queryset(self) -> Any:
        user = self.get_user()
        user = get_object_or_404(User, username=user.username)

        if self.check_users():
            return Diary.objects.filter(author=user)

        return Diary.objects.filter(author=user, is_hide=False)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Extra context:
            * owner -> it's username form url
        """
        context = super().get_context_data(**kwargs)
        context["owner"] = self.get_user().username
        return context
