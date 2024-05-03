from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ActivityLog
# Register your models here.

admin.site.register(ActivityLog)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)  # Add 'email' field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter Email Address'  # Set placeholder for username field

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)