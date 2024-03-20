from django import forms
from projects.models import Projects
from .models import DeliveryRecord
from vendor.models import WoodSupplier, WoodSource



class UploadFileForm(forms.Form):
    project_name = forms.ModelChoiceField(queryset=Projects.objects.all(), empty_label="Select a project")
    file = forms.FileField()


class DeliverySearchForm(forms.Form):
    project_id = forms.ModelChoiceField(required=False, queryset=Projects.objects.all(), empty_label="Select a project")
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY/MM/DD'}))
    vendor_name = forms.ModelChoiceField(
        queryset=WoodSupplier.objects.all(),
        to_field_name='name',
        label='Vendor Name',
        required=False
    )
    wood_source = forms.ModelChoiceField(
        queryset=WoodSource.objects.all(),
        to_field_name='location',
        label='Wood Source',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor_name'].choices = [('', 'Select Vendor')] + [(supplier.id, f"{supplier.name[:5]}... - {supplier.project}") for supplier in WoodSupplier.objects.all()]
        self.fields['wood_source'].choices = [('', 'Select Wood Source')] + [(source.id, f"{source.location[:5]}... - {source.project}") for source in WoodSource.objects.all()]


class DownloadForm(forms.Form):
    selected_data = forms.ModelMultipleChoiceField(queryset=DeliveryRecord.objects.all(), widget=forms.CheckboxSelectMultiple)


class RemarksForm(forms.Form):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))


class GraphSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY/MM/DD'}))

