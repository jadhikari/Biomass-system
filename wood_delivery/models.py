from django.db import models
from django.utils import timezone
from projects.models import Projects # Import the ProjectModel from the other app
from vendor.models import WoodSupplier, WoodSource  # Import the ProjectModel from the other app
from wood_type.models import WoodType  # Import the ProjectModel from the other app

class DeliveryRecord(models.Model):

    weighing_day = models.DateField()
    slip_no = models.IntegerField()
    woods_type = models.ForeignKey(WoodType, on_delete=models.CASCADE)
    trucks_num = models.CharField(max_length=255)
    wood_supplier = models.ForeignKey(WoodSupplier, on_delete=models.CASCADE)
    wood_sources = models.ForeignKey(WoodSource, on_delete=models.CASCADE)
    total_weight_time = models.CharField(max_length=255)
    total_weight = models.FloatField()
    empty_weight_time = models.CharField(max_length=255)
    empty_weight = models.FloatField()
    net_weight = models.FloatField()
    remarks = models.CharField(max_length=255)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=255)
    

