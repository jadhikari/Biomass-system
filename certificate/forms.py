import os
from django import forms
from vendor.models import WoodSupplier
from .models import Certificate , SupplierLogo


class CertificateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset to include only WoodSuppliers with associated logos
        self.fields['supplier_name'].queryset = WoodSupplier.objects.filter(supplierlogo__isnull=False).distinct()

    class Meta:
        model = Certificate
        fields = ['id', 'supplier_name', 'unverified_certificate']

    def __str__(self):
        return f"{self.supplier_name.project} - {self.supplier_name}"

class SupplierLogoForm(forms.ModelForm):
    supplier_name = forms.ModelChoiceField(
        queryset=WoodSupplier.objects.all(),
        label='Supplier Name'
    )

    class Meta:
        model = SupplierLogo
        fields = ['supplier_name', 'email', 'stamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_name'].queryset = WoodSupplier.objects.all()

class EditSupplierLogoForm(forms.ModelForm):
    class Meta:
        model = SupplierLogo
        fields = ['email', 'stamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'email' field non-editable
        self.fields['email'].disabled = True

class P12Form(forms.Form):
    p12_file = forms.FileField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['p12_file'].label = 'P12 File'
        self.fields['password'].label = 'Password'
        self.fields['password'].help_text = 'Enter the password for the P12 file'
        self.fields['p12_file'].help_text = 'Upload the P12 file'
        self.fields['p12_file'].widget.attrs['accept'] = '.p12'
        self.fields['p12_file'].widget.attrs['required'] = True
        self.fields['password'].widget.attrs['required'] = True

        