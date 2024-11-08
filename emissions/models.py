from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator


class Certification(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2555)

    def __str__(self):
        return self.name

class Gown(models.Model):

    name = models.CharField(max_length = 100)
    reusable = models.BooleanField()
    cost  = models.FloatField(blank = False, null = False, verbose_name="Cost per piece")
    weight = models.FloatField(blank = False, null = False, verbose_name="Weight in grams")
    certificates = models.ManyToManyField(Certification, blank=True, verbose_name='Sustainability certificates')
    washes = models.IntegerField(blank = False, null = False)
    comfort = models.IntegerField(
        validators=[
            MinValueValidator(0, message='0 - comofort is not included in the optimization.'),
            MaxValueValidator(5)
        ],
        verbose_name="Comfort level (likert scale)"
    )
    hygine = models.IntegerField(
        validators=[
            MinValueValidator(0, message='0 - hygine is not included in the optimization.'),
            MaxValueValidator(5)
        ],
        verbose_name="Hygine level (likert scale)"
    )

    def __str__(self):
        return self.name

class Emissions(models.Model):

    class EmissionStage(models.TextChoices):
        CO2 = "Co2", _("kg CO2 eq")
        ENERGY = "ENERGY", _("Energy use in MJ")
        WATER = "WATER", _("Water consumption in Liters")

    gown = models.ForeignKey('Gown', on_delete=models.CASCADE)
    emission_stage = models.CharField(max_length=255, choices=EmissionStage.choices)
    fibers = models.FloatField()
    yarn_production = models.FloatField()
    fabric_production = models.FloatField()
    finishing = models.FloatField()
    manufacturing = models.FloatField()
    packaging = models.FloatField()
    transport = models.FloatField()
    use = models.FloatField()

    @property
    def total(self):
        return (self.fibers + self.yarn_production + self.fabric_production +
                self.finishing + self.manufacturing + self.packaging +
                self.transport + self.use)

    def __str__(self):
        return f"{self.gown} {self.emission_stage}"