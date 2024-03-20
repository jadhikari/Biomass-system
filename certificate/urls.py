from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'certificate'

urlpatterns = [
    # other URL patterns
    path('verification/', views.verification, name='verification'),
    path('supplier_logo/', views.supplier_logo, name='supplier_logo'),
    path('supplier_logo/edit/<int:logo_id>/', views.edit_supplier_logo, name='edit_supplier_logo'),
    path('verify-and-edit-pdf/<int:certificate_id>/', views.verify_and_edit_pdf, name='verify_and_edit_pdf'),
    path('display-and-sign-pdf/<int:certificate_id>/', views.display_pdf_and_form, name='display_pdf_and_form'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)