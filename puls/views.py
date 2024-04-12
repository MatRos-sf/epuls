from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from epuls_tools.views import ActionType, EpulsDetailView

from .models import Puls


class PulsDetailView(LoginRequiredMixin, EpulsDetailView):
    model = Puls
    template_name = "puls/detail.html"
    slug_field = "profile__user__username"
    slug_url_kwarg = "username"
    activity = ActionType.PULS

    def get_context_data(self, **kwargs):
        """
        Extra context:
         * pulses
        :param kwargs:
        :return:
        """
        context_data = super(PulsDetailView, self).get_context_data(**kwargs)
        instance = context_data.get("object")
        is_user_account = self.check_users()
        if is_user_account:
            context_data["pulses"] = instance.pull_not_accepted_puls()

        context_data["self"] = is_user_account

        return context_data


def update_puls(request, username):
    """
    Updates the puls  values for user's profile.
    """
    pulses = request.user.profile.puls
    new_pulses = pulses.pull_not_accepted_puls()

    # Filter out non-positive values
    new_pulses = dict(filter(lambda x: x[1] > 0, new_pulses.items()))

    # Update the fields
    for key, value in new_pulses.items():
        current_value = getattr(pulses, key)
        setattr(pulses, key, current_value + int(value))

    # Save the updated object
    pulses.save()

    # Create messages
    if new_pulses:
        messages.success(request, "Your puls has been updated.")
    else:
        messages.info(request, "You have not scored any pulses.")

    # Change SinglePuls status
    pulses.pulses.filter(is_accepted=False).update(is_accepted=True)

    return redirect("account:puls", username=username)
