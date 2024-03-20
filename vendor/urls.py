from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('',views.supplier_list,name='supplier_list'),
    path('add/', views.add_supplier, name='add_supplier'),
    path('<int:id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('<int:id>/source-list/', views.source_list, name='source_list'),
    path('<int:id>/source-list/add/', views.add_source, name='add_source'),
    path('<int:supplier_id>/source-list/<int:source_id>/edit/', views.edit_source, name='edit_source'),
]
