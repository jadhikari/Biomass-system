import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone



class Projects(models.Model):
    
    def validate_image(value):
        ext = value.name.split('.')[-1].lower()
        if ext != 'jpeg' and ext != 'jpg':
            raise ValidationError('Unsupported file extension. Only jpeg,jpg files are allowed.')

    project_id = models.CharField(max_length=200, primary_key=True)
    project_name = models.CharField(max_length=200 )
    resource = models.CharField(max_length=200 )
    image = models.ImageField(upload_to='images/project/', null=True, blank=True, validators=[validate_image])
    capacity_ac = models.DecimalField(max_digits=10, decimal_places=2 )
    capacity_dc = models.DecimalField(max_digits=10, decimal_places=2)
    utility_company = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    longitude = models.CharField(max_length=20,null=True, blank=True)
    latitude = models.CharField(max_length=20,null=True, blank=True)
    altitude = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.project_id

class Equipment(models.Model):

    def validate_image(value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpeg', 'jpg']:
            raise ValidationError('Unsupported file extension. Only jpeg, jpg files are allowed.')

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    model_no = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images/equipment/', null=True, blank=True, validators=[validate_image])
    purchase_date = models.DateField()
    use_location = models.CharField(max_length=100, blank=True, null=True)
    price_with_tax = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_by = models.CharField(max_length=100)
    attachment = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)
    
    provider = models.CharField(max_length=200,null=True, blank=True)
    coverage = models.CharField(max_length=200,null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    contact = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
            return self.name
           



class Insurance(models.Model):
    
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    coverage_details = models.TextField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)

    def __str__(self):
        return str(self.equipment)

class Maintenance(models.Model):

    def validate_image(value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpeg', 'jpg']:
            raise ValidationError('Unsupported file extension. Only jpeg, jpg files are allowed.')

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, default = 1)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    next_maintenance_date = models.DateField()
    PREVENTIVE = 'Preventive Maintenance'
    CORRECTIVE = 'Corrective Maintenance'
    PREDICTIVE = 'Predictive Maintenance'
    SCHEDULED = 'Scheduled Maintenance'
    MAINTENANCE_TYPE_CHOICES = [
        (PREVENTIVE, 'Preventive Maintenance'),
        (CORRECTIVE, 'Corrective Maintenance'),
        (PREDICTIVE, 'Predictive Maintenance'),
        (SCHEDULED, 'Scheduled Maintenance'),
    ]
    maintenance_type = models.CharField(max_length=30, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    lead_by = models.CharField(max_length=100)
    TEST_RESULT_CHOICES = [
        ('OK', 'OK'),
        ('NOT_OK', 'Not OK'),
        ('OTHERS', 'Others'),
    ]
    test_result = models.CharField(max_length=8, choices=TEST_RESULT_CHOICES)
    notes = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500,blank=True, null=True)
    approval = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.project} - {self.equipment} - {self.maintenance_type}"
    

class Claim(models.Model):
    
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, default = 1)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, blank=True, null=True)
    claim_date = models.DateField()
    approve_date = models.DateField()
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    REPAIR = 'Repair'
    REPLACE = 'Replace'
    RESOLUTION_CHOICES = [
        (REPAIR, 'Repair'),
        (REPLACE, 'Replace'),
    ]
    resolution = models.CharField(max_length=7, choices=RESOLUTION_CHOICES)
    claim_type = models.CharField(max_length=100)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100)

    def clean(self):
        # Call the clean method of the superclass
        super().clean()

        # Check if approve_date is earlier than claim_date
        if self.approve_date < self.claim_date:
            raise ValidationError("Approval date cannot be earlier than claim date")
        
    def __str__(self):
        return f"{self.project} - {self.equipment} - {self.claim_type}"