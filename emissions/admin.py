from django.contrib import admin
from .models import Gown, Certification,  Emissions

admin.site.register(Certification)

class EmissionsInline(admin.TabularInline):
    model = Emissions
    extra = 0  # Number of empty forms to display

@admin.register(Gown)
class GownAdmin(admin.ModelAdmin):
    inlines = [EmissionsInline]