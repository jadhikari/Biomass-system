from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('', views.login_user, name='login_user'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout/', views.logout_user, name='logout_user'),
    path('activity-log/', views.activity_log_view, name='activity_log'),

    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='auth_app/password_reset_form.html',
            email_template_name='auth_app/password_reset_email.html',
            subject_template_name='auth_app/password_reset_subject.txt',
            success_url='/password-reset/done/'
        ),
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth_app/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth_app/password_reset_confirm.html',
            success_url='/password-reset-complete/'
        ),
        name='password_reset_confirm'),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth_app/password_reset_complete.html'
        ),
        name='password_reset_complete'),

    path('change-password/', views.change_password, name='change_password'),
]
