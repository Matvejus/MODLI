from django.contrib import admin
from django.urls import path, include
from . import views 
from django.views.generic import TemplateView

urlpatterns = [
    path("calc/", views.calculator, name = 'calculator'),
    path("entry/", TemplateView.as_view(template_name="entrypage.html"))
]
