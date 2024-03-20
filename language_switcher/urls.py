# language_switcher/urls.py

from django.urls import path
from . import views

app_name = 'switch_language'

urlpatterns = [
    path('switch-language/', views.switch_language, name='switch_language'),
]
