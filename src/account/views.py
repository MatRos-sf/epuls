from django.shortcuts import render, redirect
from .forms import UserSignupForm

def signup(request):
    form = UserSignupForm()
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    return render(request, 'account/register.html', {'form': form})