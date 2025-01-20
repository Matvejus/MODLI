from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator


class Certification(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Gown(models.Model):

    name = models.CharField(max_length = 100)
    reusable = models.BooleanField()
    cost  = models.FloatField(blank = True, null = True, verbose_name="Cost per piece €")
    laundry_cost  = models.FloatField(blank = True, null = True, verbose_name="Cost per wash €")
    weight = models.FloatField(blank = True, null = True, verbose_name="Weight in grams")
    certificates = models.ManyToManyField(Certification, blank=True, verbose_name='Sustainability certificates')
    washes = models.IntegerField(blank = True, null = True)
    comfort = models.IntegerField(
        validators=[
            MinValueValidator(0, message='0 - comofort is not included in the optimization.'),
            MaxValueValidator(6, message='6 - Not applicable')
        ],
        verbose_name="Comfort level (likert scale)"
    )
    hygine = models.IntegerField(
        validators=[
            MinValueValidator(0, message='0 - hygine is not included in the optimization.'),
            MaxValueValidator(6, message='6 - Not applicable')
        ],
        verbose_name="Hygine level (likert scale)"
    )
    source = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Emissions(models.Model):

    class EmissionStage(models.TextChoices):
        CO2 = "CO2", _("kg CO2 eq")
        ENERGY = "Energy", _("Energy use in MJ")
        WATER = "Water", _("Water consumption in Liters")
        COST = "Cost", _("Cost")
        FTE = "FTE",_("Local FTE")

    gown = models.ForeignKey('Gown', on_delete=models.CASCADE)
    emission_stage = models.CharField(max_length=255, choices=EmissionStage.choices)
    fibers = models.FloatField(blank=True, null=True)
    yarn_production = models.FloatField(blank=True, null=True)
    fabric_production = models.FloatField(blank=True, null=True)
    finishing = models.FloatField(blank=True, null=True)
    production = models.FloatField(blank=True, null=True)
    packaging = models.FloatField(blank=True, null=True)
    transport = models.FloatField(blank=True, null=True)
    use = models.FloatField(blank=True, null=True)
    lost = models.FloatField(blank=True, null=True)
    eol = models.FloatField(blank=True, null=True)

    @property
    def total(self):
        return (self.fibers + self.yarn_production + self.fabric_production +
                self.finishing + self.production + self.packaging +
                self.transport + self.use)

    def __str__(self):
        return f"{self.gown} {self.emission_stage}"