# language_switcher/views.py

from django.shortcuts import redirect
from django.urls import reverse

def switch_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language in ['en', 'jp']:
            request.session['django_language'] = language
    # Redirect to the same page or a specific page
    return redirect(request.META.get('HTTP_REFERER', '/'))