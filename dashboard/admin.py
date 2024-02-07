from django.contrib import admin
from .models import Material, Gown, CoveringMaterial, PackagingMaterial, ProductionPackagingGown, \
    LaundryTransportPackagingGown, SterilizationToHospitalPackagingGown, ProductionPackagingCoveringMaterial, \
    LaundryPackagingCoveringMaterial, SterilizationToHospitalPackagingCoveringMaterial, TransportMethod, \
    TransportToNetherlands, TransportHospitalToWashingGown, Electricity, WashingInputs, SterilizationInputs, \
    SingleUseUtilization

# Register your models here.

admin.site.register(Material)
admin.site.register(Gown)
admin.site.register(CoveringMaterial)
admin.site.register(PackagingMaterial)
admin.site.register(ProductionPackagingGown)
admin.site.register(LaundryTransportPackagingGown)
admin.site.register(SterilizationToHospitalPackagingGown)
admin.site.register(ProductionPackagingCoveringMaterial)
admin.site.register(LaundryPackagingCoveringMaterial)
admin.site.register(SterilizationToHospitalPackagingCoveringMaterial)
admin.site.register(TransportMethod)
admin.site.register(TransportToNetherlands)
admin.site.register(TransportHospitalToWashingGown)
admin.site.register(Electricity)
admin.site.register(WashingInputs)
admin.site.register(SterilizationInputs)
admin.site.register(SingleUseUtilization)
