from rest_framework import serializers
from .models import Gown, Emissions, Certification


class EmissionImpactSerializer(serializers.Serializer):
    CO2 = serializers.FloatField()
    Energy = serializers.FloatField()
    Water = serializers.FloatField()
    Cost = serializers.FloatField()
class GownSerializer(serializers.ModelSerializer):
    emission_impacts = serializers.SerializerMethodField()
    certificates = serializers.StringRelatedField(many=True)
    class Meta:
        model = Gown
        fields = ['id', 'name', 'cost', 'laundry_cost', 'washes', 'reusable', 'comfort', 'hygine', 'certificates', 'emission_impacts']

    def get_emission_impacts(self, obj):
        emissions = Emissions.objects.filter(gown=obj)

        total_emissions = {
            'CO2': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.CO2),
            'Energy': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.ENERGY),
            'Water': sum(e.total for e in emissions if e.emission_stage == Emissions.EmissionStage.WATER),
            'Cost': obj.cost
        }

        # Adjust emissions and cost if the gown is reusable
        if obj.reusable and obj.washes > 0:
            total_emissions = {key: value / obj.washes for key, value in total_emissions.items()}

        return total_emissions



class GownDetailSerializer(serializers.ModelSerializer):
    certificates = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Certification.objects.all()
    )
    class Meta:
        model = Gown
        fields = ['name', 'reusable', 'cost', 'laundry_cost', 'washes', 'comfort', 'hygine', 'certificates']

class EmissionSerializer(serializers.ModelSerializer):
    gown = serializers.StringRelatedField()
    class Meta:
        model = Emissions
        fields = ['gown', 'emission_stage', 'fibers', 'yarn_production', 'fabric_production', 'finishing', 'production', 'packaging', 'transport', 'use', 'total']
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name']