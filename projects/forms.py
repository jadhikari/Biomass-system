from datetime import datetime
from django import forms
from .models import Projects, Equipment, Insurance, Maintenance, Claim
from django.utils.safestring import mark_safe

class AddProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['project_id', 'project_name', 'resource', 'capacity_ac', 'capacity_dc', 'utility_company', 'address']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
                field.widget.attrs['required'] = True
                
    class Meta:
        model = Projects
        exclude = ['user']
        fields = ['project_id','project_name','resource', 'image', 'capacity_ac', 'capacity_dc', 'utility_company', 'address',
                  'longitude', 'latitude', 'altitude']

class EditProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['project_name', 'resource', 'capacity_ac', 'capacity_dc', 'utility_company', 'address']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
                field.widget.attrs['required'] = True
        # Disable the ID field
        self.fields['project_id'].disabled = True

    class Meta:
        model = Projects
        exclude = ['user']
        fields = ['project_id','project_name','resource', 'image', 'capacity_ac', 'capacity_dc', 'utility_company', 'address',
                  'longitude', 'latitude', 'altitude']
        

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        exclude = ['user', 'project']
        fields = ['name', 'manufacturer', 'model_no','serial_no','image','purchase_date','image','use_location', 'price_with_tax', 'purchase_by','attachment','status','remark',
                    'provider','coverage','start_date','end_date','terms','contact']  # Explicitly list the fields you want to include
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the size of attachment and remark fields
        self.fields['attachment'].widget.attrs.update({'rows': 3, 'cols': 30})
        self.fields['remark'].widget.attrs.update({'rows': 3, 'cols': 30})
        self.fields['terms'].widget.attrs.update({'rows': 3, 'cols': 30})

    def clean(self):
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get('purchase_date')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure purchase_date is not a future date
        if purchase_date and purchase_date > datetime.now().date():
            self.add_error('purchase_date', "Purchase date cannot be a future date.")

        # Ensure end_date is not earlier than start_date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "End date cannot be earlier than start date.")

        return cleaned_data
    

class InsuranceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the size of attachment and remark fields
        self.fields['coverage_details'].widget.attrs.update({'rows': 3, 'cols': 30})
    
    class Meta:
        model = Insurance
        fields = ['policy_number', 'provider', 'start_date', 'end_date', 'coverage_details', 'premium_amount', 'deductible']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure end_date is not earlier than start_date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "End date cannot be earlier than start date.")
        return cleaned_data
        

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['maintenance_date', 'next_maintenance_date', 'maintenance_type', 'image', 'lead_by', 'test_result', 'description', 'notes']
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('maintenance_date')
        end_date = cleaned_data.get('next_maintenance_date')

        # Ensure end_date is not earlier than start_date
        if start_date and end_date and end_date < start_date:
            self.add_error('next_maintenance_date', "End date cannot be earlier than start date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the size of attachment and remark fields
        self.fields['description'].widget.attrs.update({'rows': 3, 'cols': 30})

        # Set all fields except 'notes' as mandatory
        mandatory_fields = ['maintenance_date', 'next_maintenance_date', 'maintenance_type', 'image', 'lead_by', 'test_result']
        for field_name in mandatory_fields:
            self.fields[field_name].required = True


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['claim_date','approve_date','claim_amount','deductible_amount','coverage_amount','resolution','notes']
        widgets = {
            'claim_date': forms.DateInput(attrs={'type': 'date'}),
            'approve_date': forms.DateInput(attrs={'type': 'date'}),
        }
