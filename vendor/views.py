from django.shortcuts import get_object_or_404, redirect, render
from requests import request
from .models import WoodSource, WoodSupplier
from projects.models import Projects
from .form import AddSupplierForm, SupplierEditForm, AddSourceForm, EditSourceForm

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required


@login_required
@permission_required('vendor.view_woodsupplier', raise_exception=True)
def supplier_list(request):
    supplier_data = WoodSupplier.objects.all()

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Wood Supplier List', 'url': ''},    
    ]

    context = {
        'supplier_data': supplier_data,
        'breadcrumbs':breadcrumbs
    }

    return render(request, 'vendor/supplier.html', context)


@login_required
@permission_required('vendor.add_woodsupplier', raise_exception=True)
def add_supplier(request):
    error_message = None
    if request.method == 'POST':
        form = AddSupplierForm(request.POST)
        if form.is_valid():
            try:
                # Convert request.user to a string
                user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
                
                # Get the unsaved instance from the form and set the by_user field
                supplier_instance = form.save(commit=False)
                supplier_instance.user = user_string
                supplier_instance.save()

                return redirect('vendor:supplier_list')  # Replace with your actual supplier list view name
            except Exception as e:
                # Handle any errors during data save
                error_message = f"An error occurred while saving data: {str(e)}"
        else:
            # Capture form validation errors
            error_message = "Form validation error. Please correct the errors below."

    else:
        form = AddSupplierForm()


    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Wood Supplier List', 'url': '/vendor/'},
        {'name': 'Add Supplier'},  
    ]

    context = {
        'form': form, 
        'error_message': error_message,
        'breadcrumbs':breadcrumbs
    }

    return render(request, 'vendor/add_supplier.html', context)

@login_required
@permission_required('vendor.change_woodsupplier', raise_exception=True)
def edit_supplier(request, id):
    supplier = get_object_or_404(WoodSupplier, pk=id)

    if request.method == 'POST':
        form = SupplierEditForm(request.POST, instance=supplier)
        if form.is_valid():
            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            
            # Set the by_user field
            form.instance.user = user_string
            
            # Save the form data
            form.save()

            return redirect('vendor:supplier_list')

    else:
        form = SupplierEditForm(instance=supplier)

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Wood Supplier List', 'url': '/vendor/'},
        {'name': f'Id {supplier.wood_supplier_id} Edit'},  
    ]

    context = {
        'form': form, 
        'supplier': supplier,
        'breadcrumbs':breadcrumbs
    }

    return render(request, 'vendor/edit_supplier.html', context)


@login_required
@permission_required('vendor.view_woodsource', raise_exception=True)
def source_list(request, id ):
    supplier = get_object_or_404(WoodSupplier, pk=id)
    source_data = WoodSource.objects.filter(wood_supplier=supplier)
    
    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Wood Supplier List', 'url': '/vendor/'},
        {'name': f'Id {supplier.wood_supplier_id} Source List'},  
    ]

    context = {
        'supplier': supplier, 
        'source_data': source_data,
        'breadcrumbs':breadcrumbs
    }

    return render(request, 'vendor/source.html', context)

@login_required
@permission_required('vendor.add_woodsource', raise_exception=True)
def add_source(request, id):
    error_message = None

    # Get the Supplier object
    supplier = get_object_or_404(WoodSupplier, pk=id)
    if request.method == 'POST':
        form = AddSourceForm(request.POST, initial={'wood_supplier': supplier.id, 'project': supplier.project.project_id})
        if form.is_valid():
            try:
                # Save the form data with the supplier_id
                user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
                WoodSource = form.save(commit=False)
                WoodSource.user = user_string
                WoodSource.wood_supplier = supplier
                print(supplier)
                print(form.cleaned_data['project'])
                WoodSource.project = form.cleaned_data['project']
                

                WoodSource.save()
                
                return redirect('vendor:source_list', id=supplier.id)
            except Exception as e:
                # Handle any errors during data save
                error_message = f"An error occurred while saving data: {str(e)}"
        else:
            # Capture form validation errors
            error_message = "Form validation error. Please correct the errors below."

    else:
        # Initialize the form with wood_supplier as initial data
        form = AddSourceForm(initial={'wood_supplier': supplier.id,'project': supplier.project.project_id})

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Supplier List', 'url': '/vendor/'},
        {'name': f'Id {supplier.wood_supplier_id} Wood Source List', 'url': f'/vendor/{supplier.id}/source-list/'}, 
        {'name': f'Add Wood Source For Id {supplier.wood_supplier_id}'},
    ]

    context = {
        'form': form, 
        'supplier': supplier,
        'error_message': error_message,
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'vendor/add_source.html', context)

@login_required
@permission_required('vendor.change_woodsource', raise_exception=True)
def edit_source(request, source_id, supplier_id):
    source = get_object_or_404(WoodSource, pk=source_id)

    if request.method == 'POST':
        form = EditSourceForm(request.POST, instance=source)
        if form.is_valid():
            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            
            # Set the by_user field
            form.instance.user = user_string
            form.save()
            
            return redirect('vendor:source_list', id=supplier_id)
    else:
        form = EditSourceForm(instance=source)

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Supplier List', 'url': '/vendor/'},
        {'name': f'Id {supplier_id} Wood Source List', 'url': f'/vendor/{supplier_id}/source-list/'},   
        {'name': f'Edit Wood Source Id {source_id}'},
    ]

    context = {
        'form': form, 
        'source': source,
        'breadcrumbs':breadcrumbs
    }

    return render(request, 'vendor/edit_source.html', context)