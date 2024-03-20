from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login , logout
from django.contrib.auth.decorators import login_required


def login_user(request):
    if request.user.is_authenticated:
        return redirect('auth_app:welcome')  # Redirect logged-in users to the welcome page

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('auth_app:welcome')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth_app/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('auth_app:login_user')

@login_required
def welcome(request):
    return render(request, 'auth_app/welcome.html')