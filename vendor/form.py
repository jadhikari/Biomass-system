from django import forms
from .models import WoodSource, WoodSupplier
from django.utils.safestring import mark_safe

class AddSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['project','wood_supplier_id', 'name', 'registration_name', 'address','document','active']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
    class Meta:
        model = WoodSupplier
        exclude = ['user']
        fields = ['project','wood_supplier_id', 'name', 'registration_name', 'address','document','active']

    def clean_wood_supplier_id(self):
        wood_supplier_id = str(self.cleaned_data['wood_supplier_id'])  # Convert to string
        if len(wood_supplier_id) != 3 or not wood_supplier_id.isdigit():
            raise forms.ValidationError('ID must be a 3-digit number.')
        return wood_supplier_id
    
class SupplierEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['project','wood_supplier_id', 'name', 'registration_name', 'address','document','active']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
        # Disable the ID field
        self.fields['wood_supplier_id'].disabled = True
        self.fields['project'].disabled = True

    class Meta:
        model = WoodSupplier
        exclude = ['user']  # Include all fields except the ID field
        fields = ['project','wood_supplier_id', 'name', 'registration_name', 'address','document','active']
        
        

class AddSourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['project','wood_supplier','wood_source_id','location', 'registration_name', 'registration_date', 'authority', 'classification', 'removal',
                                'area', 'distance', 'document','active']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
        # Disable the ID field
        self.fields['wood_supplier'].disabled = True
        self.fields['project'].disabled = True
        #field type for date
        self.fields['registration_date'].widget = forms.DateInput(attrs={'type': 'date'})
        #field type 
        self.fields['classification'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['removal'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        #firld type for number
        self.fields['area'].widget = forms.NumberInput(attrs={'type': 'text'})
        self.fields['distance'].widget = forms.NumberInput(attrs={'type': 'text'})

    class Meta:
        model = WoodSource
        fields = ['project','wood_supplier','wood_source_id','location', 'registration_name', 'registration_date', 'authority', 'classification', 'removal',
                  'area', 'distance', 'document','active']

    def clean_wood_source_id(self):
        wood_source_id = str(self.cleaned_data['wood_source_id'])  # Convert to string
        if len(wood_source_id) != 3 or not wood_source_id.isdigit():
            raise forms.ValidationError('ID must be a 3-digit number.')
        return wood_source_id 


class EditSourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['wood_supplier','wood_source_id','location', 'registration_name', 'registration_date', 'authority', 'classification', 'removal',
                                'area', 'distance', 'document','active']:
                field.label = mark_safe(f'{field.label}<span style="color:red"> *</span>')  # Add asterisk to label of required fields and color it red
        # Disable the ID field
        self.fields['wood_supplier'].disabled = True
        self.fields['wood_source_id'].disabled = True
        #field type for date
        self.fields['registration_date'].widget = forms.DateInput(attrs={'type': 'date'})
        #field type 
        self.fields['classification'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['removal'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        #firld type for number
        self.fields['area'].widget = forms.NumberInput(attrs={'type': 'text'})
        self.fields['distance'].widget = forms.NumberInput(attrs={'type': 'text'})

    class Meta:
        model = WoodSource
        fields = ['wood_supplier','wood_source_id','location', 'registration_name', 'registration_date', 'authority', 'classification', 'removal',
                  'area', 'distance', 'document','active']

    