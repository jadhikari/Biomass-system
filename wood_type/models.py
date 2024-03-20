from django.db import models
from django.utils import timezone

class WoodType(models.Model):
    wood_id = models.IntegerField(primary_key=True, default= 1)
    wood_name = models.CharField(max_length=100 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    by_user = models.CharField(max_length=255)

