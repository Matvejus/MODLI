from rest_framework import serializers
from .models import Gown, Emissions


class EmissionImpactSerializer(serializers.Serializer):
    CO2 = serializers.FloatField()
    Energy = serializers.FloatField()
    Water = serializers.FloatField()
    Cost = serializers.FloatField()
class GownSerializer(serializers.ModelSerializer):
    emission_impacts = serializers.SerializerMethodField()
    class Meta:
        model = Gown
        fields = ['id', 'name', 'cost', 'washes', 'reusable', 'emission_impacts']

    def get_emission_impacts(self, obj):
        emissions = Emissions.objects.filter(gown=obj)
        impacts = {
            'CO2': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.CO2),
            'Energy': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.ENERGY),
            'Water': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.WATER),
            'Cost': obj.cost
        }
        return EmissionImpactSerializer(impacts).data

class GownDetailSerializer(serializers.ModelSerializer):
    certificates = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Gown
        fields = ['name', 'reusable', 'cost', 'washes', 'comfort', 'hygine', 'certificates']

class EmissionSerializer(serializers.ModelSerializer):
    gown = serializers.StringRelatedField()

    class Meta:
        model = Emissions
        fields = ['gown', 'emission_stage', 'fibers', 'yarn_production', 'fabric_production', 'finishing', 'manufacturing', 'packaging', 'transport', 'use', 'total']
