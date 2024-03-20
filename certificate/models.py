import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from vendor.models import WoodSupplier
from projects.models import Projects


def validate_pdf(value):
    ext = value.name.split('.')[-1].lower()
    if ext != 'pdf':
        raise ValidationError('Unsupported file extension. Only PNG files are allowed.')


class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    supplier_name = models.ForeignKey(WoodSupplier, on_delete=models.CASCADE )
    unverified_certificate = models.FileField(upload_to='certificates/unverified/', validators=[validate_pdf])
    verified_certificate = models.FileField(upload_to='certificates/verified/', validators=[validate_pdf])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=255)
    

    def __str__(self):
        return f"Certificate {self.id} for {self.supplier_name}"
    


def validate_png(value):
    ext = value.name.split('.')[-1].lower()
    if ext != 'png':
        raise ValidationError('Unsupported file extension. Only PNG files are allowed.')


class SupplierLogo(models.Model):
    id = models.AutoField(primary_key=True)
    wood_supplier = models.OneToOneField(WoodSupplier, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, blank=False)
    stamp = models.ImageField(upload_to='images/supplier_logos/', validators=[validate_png])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.wood_supplier}"
    
    
    


