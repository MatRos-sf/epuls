from django.views.generic.detail import DetailView

from .models import Puls


class PulsDetailView(DetailView):
    model = Puls
    template_name = "puls/detail.html"
    slug_field = "profile__user__username"
    slug_url_kwarg = "username"
