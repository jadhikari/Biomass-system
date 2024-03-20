from django.db import models
from wtforms import ValidationError
from projects.models import Projects


class WoodSupplier(models.Model):
    id =models.AutoField(primary_key=True)
    wood_supplier_id = models.IntegerField()
    name = models.CharField(max_length=200 )
    registration_name = models.CharField(max_length=200 )
    address = models.CharField(max_length=200 )
    document = models.CharField(max_length=200 )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=255)

    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.project} - {self.name} - {self.wood_supplier_id}"
     
    class Meta:
        unique_together = ('wood_supplier_id', 'project')

class WoodSource(models.Model):
    id =models.AutoField(primary_key=True)
    wood_source_id = models.IntegerField()
    location = models.CharField(max_length=200 )
    registration_date = models.DateField()
    registration_name = models.CharField(max_length=200)
    authority = models.CharField(max_length=200 )
    classification = models.CharField(max_length=200 )
    removal = models.CharField(max_length=200 )
    area = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2 )
    document = models.CharField(max_length=200)
    active = models.BooleanField(default=True )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=255)

    # Define the foreign key relationship with wood supplier
    wood_supplier = models.ForeignKey(WoodSupplier, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.wood_source_id)  # Convert to string
    
    class Meta:
        unique_together = ('project', 'wood_supplier', 'wood_source_id')
    


