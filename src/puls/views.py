from django.views.generic.detail import DetailView

from .models import Puls


class PulsDetailView(DetailView):
    model = Puls
    template_name = "puls/detail.html"
    slug_field = "profile__user__username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context_data = super(PulsDetailView, self).get_context_data(**kwargs)
        instance = context_data.get("object")
        context_data["pulses"] = instance.pull_not_accepted_puls()

        return context_data
