from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone
from django.views.generic import DetailView

from account.models import Profile, ProfileType, Visitor
from action.models import Action, ActionMessage


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "account/profile/profile.html"
    slug_field = "user__username"
    slug_url_kwarg = "username"

    def __get_user_for_path(self):
        return self.kwargs.get("username", None)

    def get_object(self, queryset=None):
        user_instance = super().get_object(queryset)

        if user_instance != self.request.user:
            # user is Visitor
            Visitor.objects.create(
                visitor=self.request.user, receiver=user_instance.user
            )

            gender = self.request.user.profile.get_gender_display().lower()
            user_instance.add_visitor(gender)

        return user_instance

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        # take last action
        context["action"] = Action.objects.filter(
            who__username=self.__get_user_for_path()
        ).first()

        # check is user's profile
        instance = context["object"]
        is_user_profile = instance.user.username == self.request.user.username
        context["self"] = is_user_profile

        # take last visitors:
        context["visitors"] = self.voyeur(instance, is_user_profile)

        return context

    def voyeur(self, profile: Profile, is_user_profile: bool) -> Optional[QuerySet]:
        """
        Returns a queryset of users who have visited the profile.
        The size of the queryset may vary depending on the profile type.
        When user is in on their own profile, they can see 5, 10, or 14 visitors depending on the profile type.
        If a user visits someone else's profile, they can see 0, 5, 10, 14 visitors depending on the profile type.
        """
        list_of_visitors_size = (5, 10, 14, 14) if is_user_profile else (0, 5, 10, 14)
        list_of_profile_type: List[str] = [t[0] for t in ProfileType.choices]

        login_user_profile_type = self.request.user.profile.type_of_profile
        size: int = list_of_visitors_size[
            list_of_profile_type.index(login_user_profile_type)
        ]

        return Visitor.get_visitor(profile.user, size) if size else None

    def __action(self, activity: str = "PROFILE") -> None:
        username = self.kwargs.get("username")
        whom = User.objects.get(username=username)
        is_own_action = self.request.user == whom
        if is_own_action:
            whom = None
        action = (
            getattr(ActionMessage, f"OWN_{activity}")
            if is_own_action
            else getattr(ActionMessage, f"SB_{activity}")
        )

        last_action = Action.objects.filter(who=self.request.user).first()

        if not last_action:
            Action.objects.create(who=self.request.user, action=action, whom=whom)
        elif last_action.action == action:
            last_action.date = timezone.now()
            last_action.save(update_fields=["date"])
        else:
            Action.objects.create(who=self.request.user, whom=whom, action=action)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        self.__action()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # delete profile picture
        profile = self.get_object().profile
        profile.delete_profile_picture()
        return self.get(request, *args, **kwargs)


__all__ = ["ProfileView"]
