from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
def list_events(request):

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Events', 'url': ''},    
    ]

    context = {
        'breadcrumbs':breadcrumbs
    }
    return render(request, 'event/index.html', context)

