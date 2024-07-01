from django.db import models
from django.utils.translation import gettext_lazy as _



class Certification(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2555)

    def __str__(self):
        return self.name


class Gown(models.Model):

    name = models.CharField(max_length = 100)
    reusable = models.BooleanField()
    nre_emissions = models.FloatField(blank = False, null = False,)
    co2 = models.FloatField(blank = False, null = False)
    blue_water = models.FloatField(blank = False, null = False)
    solid_waste = models.FloatField(blank = False, null = False)
    cost  = models.FloatField(blank = False, null = False)
    certificates = models.ManyToManyField(Certification, blank=True)
    washes = models.IntegerField(blank = False, null = False)

    def __str__(self):
        return self.name
    
class Co22(models.Model):
    
    gown = models.ForeignKey(Gown, on_delete = models.CASCADE)
    fibers = models.FloatField()
    yarn_production = models.FloatField()
    fabric_production = models.FloatField()
    finishing = models.FloatField()
    manufacturing = models.FloatField()
    packaging = models.FloatField()
    transport = models.FloatField()
    use = models.FloatField()
    end_of_life = models.FloatField()
    
class Energy(models.Model):
    
    gown = models.ForeignKey(Gown, on_delete = models.CASCADE)
    fibers = models.FloatField()
    yarn_production = models.FloatField()
    fabric_production = models.FloatField()
    finishing = models.FloatField()
    manufacturing = models.FloatField()
    packaging = models.FloatField()
    transport = models.FloatField()
    use = models.FloatField()
    end_of_life = models.FloatField()
    
class Water(models.Model):
    
    gown = models.ForeignKey(Gown, on_delete = models.CASCADE)
    fibers = models.FloatField()
    yarn_production = models.FloatField()
    fabric_production = models.FloatField()
    finishing = models.FloatField()
    manufacturing = models.FloatField()
    packaging = models.FloatField()
    transport = models.FloatField()
    use = models.FloatField()
    end_of_life = models.FloatField()







