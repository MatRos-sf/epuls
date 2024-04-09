from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from account.models import TYPE_OF_PROFILE, Profile, Visitor
from action.models import Action
from epuls_tools.views import ActionType, EpulsDetailView

__all__ = ["ProfileView"]


class ProfileView(LoginRequiredMixin, EpulsDetailView):
    model = Profile
    template_name = "account/profile/profile.html"
    slug_field = "user__username"
    slug_url_kwarg = "username"
    activity = ActionType.PROFILE

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Extra context:
            * action: (Action) last user's Action
            * self: (bool)  is current user's profile
            * visitors: (List[Visitor]) list of last visitors
        """
        context = super(ProfileView, self).get_context_data(**kwargs)

        # get profile from object -> object.user.username == self.kwargs.get("username")
        instance_user = self.url_user()

        # take last action
        context["action"] = Action.last_user_action(instance_user)

        # if it's currently login user's profile, then set True
        is_login_user = self.check_users()
        context["self"] = is_login_user

        # take last visitors:
        context["visitors"] = self.voyeur(instance_user.profile, is_login_user)

        return context

    def voyeur(self, profile: Profile, is_user_profile: bool) -> Optional[QuerySet]:
        """
        Returns a queryset of users who have visited the profile.
        The size of the queryset may vary depending on the profile type.
        When user is in on their own profile, they can see 5, 10, or 14 visitors depending on the profile type.
        If a user visits someone else's profile, they can see 0, 5, 10, 14 visitors depending on the profile type.
        """
        profile_type = self.login_user().profile.type_of_profile

        size: int = TYPE_OF_PROFILE[profile_type][
            "own_visitors" if is_user_profile else "sb_visitors"
        ]

        return Visitor.get_visitor(profile.user, size) if size else None

    def post(self, request, *args, **kwargs):
        # delete profile picture
        # TODO zobacz czy test inny nie usunie foty
        profile = self.get_object()
        if self.request.user == profile.user:
            profile.delete_profile_picture()
            messages.success(request, "Profile picture has been deleted.")
        else:
            messages.error(
                request,
                "You can't delete profile picture because you are not the owner of this profile.",
            )
        return self.get(request, *args, **kwargs)
