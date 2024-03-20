from django.urls import path
from . import views

app_name = 'wood_delivery'

urlpatterns = [
    path('',views.index,name='index'),
    path('upload-csv',views.upload_csv,name='upload_csv'),
    path('download_certificate/', views.download_certificate, name='download_certificate'),
    path('<int:entry_id>/details/', views.details_page, name='details_page'),
    path('api_graph/', views.api_graph, name='api_graph'),
]
