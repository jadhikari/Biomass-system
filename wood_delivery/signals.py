import os
from django.dispatch import Signal
from certificate.models import Certificate , SupplierLogo
from wood_delivery.models import  DeliveryRecord
# Define a custom signal
non_duplicate_data_uploaded = Signal()


# Define a custom exception for when no supplier logo is found
class SupplierLogoNotFoundError(Exception):
    pass


# Define a receiver function to handle the signal
def handle_non_duplicate_data(sender, non_duplicate_rows, **kwargs):
    print("\nReceived non-duplicate data signal:")
    for entry in non_duplicate_rows:
        print(f"Processing entry with id: {entry.id}")
        try:
            # Check if the delivery_record id exists in Certificate model
            certificate = Certificate.objects.get(delivery_record_id=entry.id)
            print(f"Certificate found for delivery record {entry.id}")
            
            # Obtain the wood_supplier associated with the certificate
            wood_supplier = certificate.supplier_name
            print(f"Wood supplier associated with certificate: {wood_supplier}")
            
            # Now you can perform any additional actions using wood_supplier
            
        except Certificate.DoesNotExist:
            print(f"No certificate found for delivery record {entry.id}")
            try:
                # If certificate not found, check the supplier_id from DeliveryRecord
                delivery_record = DeliveryRecord.objects.get(id=entry.id)
                print(f"Delivery record found with id {entry.id}")
                
                # Obtain the wood_supplier associated with the delivery record
                user = delivery_record.user
                wood_supplier = delivery_record.wood_supplier
                print(f"Wood supplier associated with delivery record: {wood_supplier}")
                
                # Check if the wood_supplier ID exists in SupplierLogo model
                try:
                    supplier_logo = SupplierLogo.objects.get(wood_supplier_id=wood_supplier.id)
                    print(f"Supplier logo found for wood supplier {wood_supplier.id}")
                    # Now you can perform any additional actions using supplier_logo
                    
                    # Generate path for the PDF file
                    pdf_path = f"certificates/unverified/{entry.id}.pdf"
                    
                    
                    certificate = Certificate.objects.create(
                        supplier_name=wood_supplier,
                        delivery_record=entry,
                        unverified_certificate=pdf_path,
                        user= user
                    )
                    
                    print(f"Certificate created with id: {certificate.id}")
                    
                except SupplierLogo.DoesNotExist:
                    print(f"No supplier logo found for wood supplier {wood_supplier.id}")
                    raise SupplierLogoNotFoundError(f"No supplier logo found for wood supplier {wood_supplier.id}")
                
            except DeliveryRecord.DoesNotExist:
                print(f"No delivery record found with id {entry.id}")

        except FileNotFoundError as e:
            print(e)  # Print the error message
            # Skip further processing for this entry
            continue



# Connect the receiver function to the signal
non_duplicate_data_uploaded.connect(handle_non_duplicate_data)
