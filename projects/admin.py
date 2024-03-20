from django.contrib import admin
from .models import Projects, Equipment, Insurance, Maintenance, Claim
# Register your models here.

admin.site.register(Projects)
admin.site.register(Equipment)
admin.site.register(Insurance)
admin.site.register(Maintenance)
admin.site.register(Claim)
