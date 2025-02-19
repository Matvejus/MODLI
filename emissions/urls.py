from django.contrib import admin
from django.urls import path, include
from . import views 
from django.views.generic import TemplateView



urlpatterns = [
    path('gowns/', views.gown_list, name='gown_list'),
    path('gowns/<int:pk>/', views.gown_detail, name='gown_detail'),
    path('gowns/<int:gown_id>/save/', views.save_gown_session, name='save_gown_session'),
    # path('gowns/<int:gown_id>/session/', views.get_gown_session, name='get_gown_session'),
    path('gowns/<int:pk>/emissions/', views.gown_emissions, name='gown_emissions'),
    path('api/opt/', views.optimize_gowns_api, name='optimize_gowns_api'),
    path('api/selected-gowns-emissions/', views.selected_gowns_emissions, name='selected_gowns_emissions'),
    path('certificates/', views.all_certificates, name='all_certificates'),
    path('api/certifications/', views.CertificationView.as_view(), name='certification-create'),
    path('api/certifications/<int:pk>/', views.CertificationView.as_view(), name='certification-update-delete'),
]