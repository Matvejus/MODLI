from django.db import models
from django.utils.translation import gettext_lazy as _


class Material(models.Model):
    name = models.CharField(max_length = 100, blank = False)
    component_1 = models.CharField(max_length = 100, blank = True, null = True)
    component_1_percent = models.FloatField(blank = True, null = True)
    component_2 = models.CharField(max_length = 100, blank = True, null = True)
    component_2_percent = models.FloatField(blank = True, null = True)
    description = models.CharField(max_length = 255, blank = True)

    def __str__(self):
        return self.name


class Gown(models.Model):
    name = models.CharField(max_length = 100, blank = False, null = False)
    reusable = models.BooleanField()
    times_reused = models.IntegerField(blank = True, null = True)
    weight = models.FloatField(blank = False, null = False)
    materials_v1 = models.ManyToManyField(Material, related_name="materials_v1")
    materials_v2 = models.ManyToManyField(Material, blank=True, related_name="materials_v2")

    def __str__(self):
        return self.name


class CoveringMaterial(models.Model):

    class AdhesiveEdge(models.TextChoices):
        #choices for adhesive edge of the gown
        LPE = "LPE", _("Loose polyester edge")
        MIDDLE = "LPEE", _("Loose polyesterene edge")
        END = "FIXED", _("Fixed edge")

    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    times_reused = models.IntegerField(blank = True, null=True )
    surface = models.FloatField(blank = False)
    weight = models.FloatField(blank = False, null = False)
    materials = models.ManyToManyField(Material, related_name = "materials_coveringmaterials")
    adhisive_edge = models.CharField(max_length = 100, blank = True, choices = AdhesiveEdge.choices)

    def __str__(self):
        return str(self.gown.name)
    

class PackagingMaterial(models.Model):
    name = models.CharField(max_length = 100, blank = False)
    recycled = models.BooleanField(blank = False)

    def __str__(self):
        return self.name


class ProductionPackagingGown(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    primary_material = models.ManyToManyField(PackagingMaterial, related_name="production_packaging_gown_primary_material")
    primary_weight = models.IntegerField(blank = True, null = True)
    primary_quantity = models.IntegerField(blank = True, null = True)
    secondary_material = models.ManyToManyField(PackagingMaterial, blank = True, related_name="production_packaging_gown_secondary_material")
    secondary_weight = models.IntegerField(blank = True, null = True)
    secondary_quantity = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return str(self.gown.name)
    
class LaundryTransportPackagingGown(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    material = models.ManyToManyField(PackagingMaterial, related_name = "laundry_transport_packaging_gown")
    weight = models.FloatField(blank = False)
    quantity = models.IntegerField(blank = False)

    def __str__(self):
        return str(self.gown.name)


class SterilizationToHospitalPackagingGown(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE, verbose_name="Gown")
    sterilization_paper = models.BooleanField(blank=True)
    primary_material = models.ManyToManyField(PackagingMaterial, related_name='primary_material')
    primary_weight = models.IntegerField(blank=False)
    primary_quantity = models.IntegerField(blank=False)
    secondary_material = models.ManyToManyField(PackagingMaterial, related_name='secondary_material', blank=True)
    secondary_weight = models.IntegerField(blank=True, null=True)
    secondary_quantity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.gown.name)


class ProductionPackagingCoveringMaterial(models.Model):
    covering_material = models.ForeignKey(CoveringMaterial, on_delete=models.CASCADE)
    primary_material = models.ManyToManyField(PackagingMaterial, related_name='production_packaging_covering_material_primary')
    primary_weight = models.IntegerField(blank=False)
    primary_quantity = models.IntegerField(blank=False)
    secondary_material = models.ManyToManyField(PackagingMaterial, related_name='production_packaging_covering_material_secondary', blank=True)
    secondary_weight = models.IntegerField(blank=True, null=True)
    secondary_quantity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.covering_material.gown.name)

    

class LaundryPackagingCoveringMaterial(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE,)#not sure
    covering_material = models.ForeignKey(CoveringMaterial, on_delete=models.CASCADE, blank = True, null = True)
    material = models.ManyToManyField(PackagingMaterial)
    weight = models.FloatField(blank = False)
    quantity = models.IntegerField(blank = False)

    def __str__(self):
        return str(self.gown.name)


class SterilizationToHospitalPackagingCoveringMaterial(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    covering_material = models.ForeignKey(CoveringMaterial, on_delete=models.CASCADE, blank=True)
    material = models.ManyToManyField(PackagingMaterial, related_name='sterilization_to_hospital_covering_material_packaging')

    def __str__(self):
        return str(self.gown.name )


class TransportMethod(models.Model):

    class Fuel(models.TextChoices):
        DIESEL = "DIESEL", _("Diesel")
        PETROL = "PETROL", _("Petrol")
        LNG = "LNG", _("Liquefied natural gas")
        ELECTR = "ELECTR", _("Electric")

    transport = models.CharField(max_length = 100, blank = True, null = True)
    tonnage = models.IntegerField(blank = True, null = True)
    fuel = models.CharField(max_length = 100, blank = True, null = True, choices = Fuel.choices)

    def __str__(self):
        return f"{self.transport}/{self.tonnage}/{self.fuel}   "


class TransportToNetherlands(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE,)#not sure
    covering_material = models.ForeignKey(CoveringMaterial, on_delete=models.CASCADE, blank = True)#not sure
    country_of_origin = models.CharField(max_length = 100, blank = True)
    transport_1 = models.ForeignKey(TransportMethod, blank = True, null = True, on_delete = models.DO_NOTHING, related_name = "transport_to_netherlands_1")
    distance_1 = models.IntegerField(blank = True, null = True)
    transport_2 = models.ForeignKey(TransportMethod, blank= True, null = True, on_delete = models.DO_NOTHING, related_name = "transport_to_netherlands_2")
    distance_2 = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return str(self.gown.name)


class TransportHospitalToWashingGown(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE,)#not sure
    transport = models.ForeignKey(TransportMethod, on_delete = models.DO_NOTHING)
    distance = models.IntegerField(blank = False)

    def __str__(self):
        return str(self.gown.name)


class Electricity(models.Model):
    country = models.CharField(max_length = 100, blank = False)

    def __str__(self):
        return self.country
    

class WashingInputs(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    electricity = models.ForeignKey(Electricity, on_delete = models.DO_NOTHING)
    natural_gas = models.FloatField(blank = False)
    water = models.FloatField(blank = False)
    demineralized_water = models.FloatField(blank = False)
    detergent = models.FloatField(blank = False)

    def __str__(self):
        return str(self.gown.name)


class SterilizationInputs(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE)
    electricity = models.ForeignKey(Electricity, on_delete = models.DO_NOTHING)
    natural_gas = models.FloatField(blank = False)
    ethylene_oxide = models.FloatField(blank = True, null = True)
    nitrogen = models.FloatField(blank = False)
    water = models.FloatField(blank = False)

    def __str__(self):
        return str(self.gown.name)

class SingleUseUtilization(models.Model):
    gown = models.ForeignKey(Gown, on_delete=models.CASCADE )
    electricity = models.ForeignKey(Electricity, on_delete=models.CASCADE)
    heat = models.FloatField(blank = False)
    electrical_efficiency = models.IntegerField(blank = False)
    thermal_efficiency = models.IntegerField(blank = False )

    def __str__(self):
        return str(self.gown.name)



class Production(models.Model):
    gown = models.ForeignKey(Gown, on_delete = models.CASCADE)
    covering_material = models.ForeignKey(CoveringMaterial, on_delete = models.CASCADE)
    




class Washing(models.Model):
    pass

class Hospital(models.Model):
    pass

class EndOfUse(models.Model):
    pass 


    





