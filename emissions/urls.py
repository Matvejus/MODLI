from django.contrib import admin
from django.urls import path, include
from . import views 
from django.views.generic import TemplateView



urlpatterns = [
    path("calc/", views.calculator, name = 'calculator'),
    path("compare/", views.compare, name = 'compare'),
    path("entry/", views.gowns, name='gown_list'),
    path('gown/edit/<int:id>/', views.gown_edit, name='gown_edit'),
    path('scenario1/', views.scenario1, name = 'scenario1' ),
    path('gowns/', views.gown_list, name='gown_list'),
    path('gowns/<int:pk>/', views.gown_detail, name='gown_detail'),
    path('gowns/<int:pk>/emissions/', views.gown_emissions, name='gown_emissions'),
    path('api/opt/', views.optimize_gowns_api, name='optimize_gowns_api'),
    path('api/debug/', views.optimize_gowns, name='optimize_gowns'),

]
