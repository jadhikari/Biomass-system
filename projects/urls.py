from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add-project/', views.AddProjectView.as_view(), name='add_project'),
    path('<str:project_id>/edit/', views.EditProjectView.as_view(), name='edit_project'),
    path('<str:project_id>/detail/', views.ProjectDetailsView.as_view(), name='project_details'),
    path('<str:project_id>/add-equipment/', views.EquipmentAddView.as_view(), name='add_equipment'),
    path('<str:project_id>/edit-equipment/<str:id>/', views.EquipmentEditView.as_view(), name='edit_equipment'),
    path('<str:project_id>/equipment-detail/<str:id>/', views.EquipmentDetailsView.as_view(), name='equipment_detail'),
    path('<str:project_id>/add-insurance/<str:id>/', views.InsuranceAddView.as_view(), name='add_insurance'),
    path('<str:project_id>/edit-insurance/<str:id>/', views.InsuranceEditView.as_view(), name='edit_insurance'),
    path('<str:project_id>/add-maintenance/<str:equipment_id>/', views.AddMaintenanceView.as_view(), name='add_maintenance'),
    path('<str:project_id>/maintenance/<str:equipment_id>/<str:maintenance_id>/', views.MaintenanceDetailsView.as_view(), name='maintenance_details'),
    path('<str:project_id>/equipment-edit/<str:equipment_id>/maintenance-detail/<str:maintenance_id>/edit/', views.MaintenanceEditView.as_view(), name='maintenance_edit'),
    path('<str:project_id>/add-claim/<str:equipment_id>/<str:insurance_id>/', views.AddClaimView.as_view(), name='add_claim'),
    path('<str:project_id>/w-claim/<str:equipment_id>/', views.AddWClaimView.as_view(), name='w_claim'),
]