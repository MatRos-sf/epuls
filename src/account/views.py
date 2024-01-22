from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm
from django.views.generic import DetailView

from .models import Profile, Visitor
from django.contrib.auth.models import User


def signup(request) -> HttpResponse:
    form = UserSignupForm()
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    return render(request, 'account/forms.html', {'form': form, 'title': 'Sign Up'})

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'account/profile.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('slag')
        user_instance = get_object_or_404(User, username=username)
        if user_instance != self.request.user.username:
            # user is Visitor
            Visitor.objects.create(visitor=self.request.user, receiver=user_instance)
        return user_instance

