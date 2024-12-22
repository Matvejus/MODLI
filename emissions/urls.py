from django.contrib import admin
from django.urls import path, include
from . import views 
from django.views.generic import TemplateView



urlpatterns = [

    path('gowns/', views.gown_list, name='gown_list'),
    path('gowns/<int:pk>/', views.gown_detail, name='gown_detail'),
    path('gowns/<int:pk>/emissions/', views.gown_emissions, name='gown_emissions'),
    path('api/opt/', views.optimize_gowns_api, name='optimize_gowns_api'),
    path('gown_emissions/', views.GownEmissionsAPIView.as_view(), name='gown_emissions'),
    path('api/selected-gowns-emissions/', views.selected_gowns_emissions, name='selected_gowns_emissions'),
    path('certificates/', views.all_certificates, name='all_certificates'),

]