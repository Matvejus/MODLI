from django.db import models
from django.utils.translation import gettext_lazy as _

class Gown(models.Model):
    name = models.CharField(max_length = 100)
    reusable = models.BooleanField()
    nre_emissions = models.FloatField(blank = False, null = False,)
    co2 = models.FloatField(blank = False, null = False)
    blue_water = models.FloatField(blank = False, null = False)
    solid_waste = models.FloatField(blank = False, null = False)

    def __str__(self):
        return self.name







