from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from datetime import datetime
import os
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .forms import CertificateForm, EditSupplierLogoForm, P12Form, SupplierLogoForm
from .models import Certificate, SupplierLogo
from vendor.models import WoodSupplier
from django.utils.translation import gettext as _
from endesive.pdf import cms


@login_required
@permission_required('certificate.view_certificate', raise_exception=True)
def verification(request):
    all_users = User.objects.all()
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string

            try:
                form.save()
                messages.success(request, 'Certificate saved successfully.')
                return redirect('certificate:verification')  # Redirect to the verification page
            except Exception as e:
                print(f"Error saving the verification: {e}")
                messages.error(request, f'Error saving the verification. {e}')
        else:
            print(form.errors)  # Print form errors to console
            messages.error(request, 'Error saving the certificate. Please check the file.')
    else:
        form = CertificateForm()

    
    certificates = Certificate.objects.all()
    supplierLogos = SupplierLogo.objects.all()
    filtered_certificates = []

    # Extract usernames from all_users and supplierLogos
    all_users_usernames = {str(user) for user in all_users}
    #print(all_users_usernames)
    supplier_logos_usernames = {supplierLogo.email for supplierLogo in supplierLogos}
    #print(supplier_logos_usernames)
    # Find matching usernames
    matching_usernames = list(all_users_usernames & supplier_logos_usernames)
    #print(matching_usernames)
    # Find non-matching usernames
    non_matching_usernames_all_users = list(all_users_usernames - supplier_logos_usernames)
    #print(non_matching_usernames_all_users)
    # Filter certificates
    for supplierLogo in supplierLogos:
        for matching_username in matching_usernames:
            #username = supplierLogo.email.split('@')[0]
            if matching_username == supplierLogo.email == str(request.user):
                #print (f'{matching_username} == {username}')
                for certificate in certificates:
                    if certificate.supplier_name == supplierLogo.wood_supplier:
                        #print (f'{certificate.supplier_name} == {supplierLogo.wood_supplier}')
                        filtered_certificates.append(certificate)

    for supplierLogo in supplierLogos:
        #username = supplierLogo.email.split('@')[0]
        for non_matching_username in non_matching_usernames_all_users:
            #print(non_matching_username)
            if supplierLogo.email != non_matching_username == str(request.user):
                for certificate in certificates:
                    # Clear the filtered_certificates list
                    filtered_certificates.clear()
                    filtered_certificates.extend(certificates)

    # Sort filtered certificates by ID in reverse order
    filtered_certificates.sort(key=lambda x: x.id, reverse=True)





    verification_list_name = _("Verification List")
    
    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': verification_list_name, 'url': '/certificate/verification/'},    
    ]

    context = {
        'filtered_certificates': filtered_certificates, 
        'supplierLogos': supplierLogos,
        'form': form,
        'breadcrumbs':breadcrumbs
    }
    

    return render(request, 'certificate/verification.html', context)


@login_required  
@permission_required('certificate.change_certificate', raise_exception=True)
def verify_and_edit_pdf(request, certificate_id, p12, password):
    """Supplier verifies PDF and attach uploaded p12/pfx for signature.

    Editable:
    - Signature field
    - Signature box
    - Signature image
    - Signature reason
    - Signature location
    - Signature contact
    - Signature date
    Args:
        request (HttpRequest): The HTTP request object
        certificate_id (int): The ID of the certificate
        p12 (bytes): The P12 file content
        password (str): The password for the P12 file
    Returns:
        HttpResponse: The HTTP response object
    """
    cert = get_object_or_404(Certificate, id=certificate_id)
    certificate_supplier_name_id = cert.supplier_name
    
    user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
    cert.user = user_string

    # Step 2: Retrieve Certificate and Stamp
    edit_certificate_path = cert.unverified_certificate.path
    supplier_logo = get_object_or_404(SupplierLogo, wood_supplier=certificate_supplier_name_id)
    stamp_path = supplier_logo.stamp.path
    
    # Print paths for verification
    print("Edit Certificate Path:", edit_certificate_path)
    print("Supplier Logo Path:", stamp_path)

    

    new_pdf_directory = os.path.join(settings.MEDIA_ROOT, 'certificates', 'verified')
    # Step 3: Generate a New PDF
    os.makedirs(new_pdf_directory,exist_ok= True) 
    new_pdf_path = os.path.join(new_pdf_directory, f'{certificate_supplier_name_id}_verified.pdf')

    # Use os.path.join for constructing paths
    new_pdf_path = os.path.normpath(new_pdf_path)
    

    date_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    dct = {
        "aligned": 0,
        "sigflags": 1,
        "sigflagsft": 132,
        "sigpage": 0,
        "sigbutton": True,
        "sigfield": "Signature1",
        "sigandcertify": True,
        "signaturebox": (523, 573, 573, 623),
        "signature_img": stamp_path,
        "contact": "email",
        "location": "region",
        "signingdate": date_time_str,
        "reason": "To execute/formalize/affirm the contract",
        "password": password,
    }
    password_bytes = bytes(password, 'utf-8')
    private_key, cert, additional_certificates = load_key_and_certificates(p12, password_bytes, default_backend())
    file_name = edit_certificate_path
    pdf_data = open(file_name, "rb").read()
    sign_pdf_data = cms.sign(pdf_data, dct, private_key, cert, additional_certificates, "sha256")
    file_name = new_pdf_path
    with open(file_name, "wb") as fp:
        fp.write(pdf_data)
        fp.write(sign_pdf_data)
    # # Update the Certificate model with the new PDF
    pdf_filename = f'{date_time_str}_verified.pdf'
    # # Use File context manager to handle file operations
    with open(new_pdf_path, 'rb') as verified_certificate_file:
        data = File(verified_certificate_file)
        certificate = Certificate.objects.get(id=certificate_id)
        certificate.verified_certificate.save(pdf_filename, data, save=True)
    return redirect('certificate:verification')



@login_required
@permission_required('certificate.view_supplierlogo', raise_exception=True)
def supplier_logo(request):
    if request.method == 'POST':
        form = SupplierLogoForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            
            # Retrieve the selected supplier name from the form
            supplier_name = form.cleaned_data.get('supplier_name')
            if supplier_name:
                try:
                    project_id = supplier_name.project_id
                    wood_supplier_id = supplier_name.wood_supplier_id

                    # Query the WoodSupplier instance based on the extracted components
                    wood_supplier_query = WoodSupplier.objects.filter(project__project_id=project_id, wood_supplier_id=wood_supplier_id)

                    print("WoodSupplier Queryset:", wood_supplier_query)

                    wood_supplier = wood_supplier_query.first()

                    if wood_supplier:
                        form.instance.wood_supplier = wood_supplier
                    else:
                        # Handle the case where no matching WoodSupplier instance is found
                        messages.error(request, 'Selected supplier does not exist.')
                        return redirect('certificate:supplier_logo')

                except WoodSupplier.DoesNotExist:
                    # Handle the case where no matching WoodSupplier instance is found
                    messages.error(request, 'Selected supplier does not exist.')
                    return redirect('certificate:supplier_logo')

            try:
                form.save()
                messages.success(request, 'Supplier logo saved successfully.')
                return redirect('certificate:supplier_logo')  # Redirect to the supplier logo list view
            except Exception as e:
                print(f"Error saving the supplier logo: {e}")
                messages.error(request, f'Error saving the supplier logo. {e}')
        else:
            print(form.errors)  # Print form errors to console
            messages.error(request, 'Error to save the supplier logo. Please check the form.')
    else:
        form = SupplierLogoForm()
        
    logos = SupplierLogo.objects.all()

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Supplier Logo'},    
    ]

    context = {
        'form': form, 
        'logos': logos,
        'breadcrumbs': breadcrumbs
    }
    
    return render(request, 'certificate/supplier_logo.html', context)




@login_required
@permission_required('certificate.change_supplierlogo', raise_exception=True)
def edit_supplier_logo(request, logo_id):
    logo = get_object_or_404(SupplierLogo, id=logo_id)

    if request.method == 'POST':
        form = EditSupplierLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.user = user_string
            try:
                form.save()
                messages.success(request, 'Supplier logo updated successfully.')
                return redirect('certificate:supplier_logo')  # Redirect to the supplier logo list view
            except Exception as e:
                print(f"Error updating the supplier logo: {e}")
                messages.error(request, f'Error in updating the supplier logo. {e}')
        else:
            messages.error(request, 'Error updating the supplier logo. Please check the form.')
    else:
        form = EditSupplierLogoForm(instance=logo)

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Supplier Logo', 'url': '/certificate/supplier_logo/'}, 
        {'name': f'Edit ID {logo_id}', 'url': f'/certificate/supplier_logo/edit/{logo_id}/'},    
    ]

    context = {
        'form': form, 
        'logo': logo,
        'breadcrumbs':breadcrumbs
    }
    
    return render(request, 'certificate/edit_supplier_logo.html', context)


@xframe_options_sameorigin
@login_required
@permission_required('certificate.view_certificate', raise_exception=True)
def display_pdf_and_form(request, certificate_id):
    """ Display the PDF file and form for uploading the P12 file and password.
    Not compatible with browsers that block X-Frame-Options.
    X-Frame-Options should be enabled if Embedding pdf is needed.

    Args:
        request (HttpRequest): The HTTP request object
        certificate_id (int): The ID of the certificate

    Returns:
        HttpResponse: The HTTP response object
        p12_file (bytes): The P12 file content
        password (str): The password for the P12 file
"""
    # Get the certificate
    certificate = get_object_or_404(Certificate, pk=certificate_id)

    # Create a new form instance
    form = P12Form()

    # If this is a POST request, process the form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = P12Form(request.POST, request.FILES)

        # Check if the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data
            # This is where you would handle the uploaded p12 file and password
            p12_file = form.cleaned_data['p12_file']
            password = form.cleaned_data['password']
            p12_file_content = p12_file.read()
            verify_and_edit_pdf(request, certificate_id, p12_file_content, password)
            return redirect('certificate:verification')

    # Open the PDF file associated with the certificate
    pdf_url = certificate.unverified_certificate.url
    print(pdf_url)
    verification_list_name = _("Verification List")
    verification_form = _("Verification Form")
    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': verification_list_name, 'url': '/certificate/verification/'},  
        {'name': verification_form}  
    ]

    context = {
        'certificate': certificate, 
        'pdf_url': pdf_url,
        'form': form,
        'breadcrumbs':breadcrumbs
    }

    # Render the form with the PDF file
    return render(request, 'certificate/display_pdf_and_form.html', context)