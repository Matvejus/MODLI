from django.contrib import admin
from .models import Gown, Certification,  Emissions, Specification, Envpar, Stages

admin.site.register(Gown)
admin.site.register(Certification)
admin.site.register(Emissions)
admin.site.register(Specification)
admin.site.register(Envpar)
admin.site.register(Stages)
