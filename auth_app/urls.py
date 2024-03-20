from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

app_name = 'auth_app'

urlpatterns = [
    path('', views.login_user, name='login_user'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout/', views.logout_user, name='logout_user'),
    path('accounts/', include('django.contrib.auth.urls')),
   
]