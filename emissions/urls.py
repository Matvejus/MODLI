from django.contrib import admin
from django.urls import path, include
from . import views 
from django.views.generic import TemplateView

urlpatterns = [
    path("calc/", views.calculator, name = 'calculator'),
    path("compare/", views.compare, name = 'compare'),
    path("entry/", views.gown_list, name='gown_list'),
    path('gown/edit/<int:id>/', views.gown_edit, name='gown_edit'),

]
