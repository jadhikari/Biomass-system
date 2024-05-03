from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login , logout
from django.contrib.auth.decorators import login_required
from .models import ActivityLog

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



@login_required
def activity_log_view(request):

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'User Logs', 'url': ''},    
    ]

    if not request.user.is_superuser:
        error ="You do not have permission to access this page."
        context = {
        'breadcrumbs': breadcrumbs,
        'error':error
        }

        return render(request, 'auth_app/activity_log.html', context)
    logs = ActivityLog.objects.all().order_by('-timestamp')  # Retrieve all logs, ordered by timestamp
    context = {
        'breadcrumbs': breadcrumbs,
        'logs':logs
        }
    return render(request, 'auth_app/activity_log.html', context)


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('auth_app:welcome')
    else:
        form = PasswordChangeForm(user=request.user, )
    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Change Password'},    
    ]
    context = {
        'breadcrumbs': breadcrumbs,
        'form':form
        }
    return render(request, 'auth_app/change_password.html', context)