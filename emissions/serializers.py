from rest_framework import serializers
from .models import Gown, Emissions


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
        fields = [
            'id', 'name', 'cost', 'washes', 'reusable', 
            'comfort', 'hygine', 'certificates', 
            'emission_impacts'
        ]

    def get_emission_impacts(self, obj):
        emissions = Emissions.objects.filter(gown=obj)

        # Initialize dictionaries for total and per-stage emissions
        total_emissions = {
            'CO2': 0, 'Energy': 0, 'Water': 0, 'Cost': obj.cost
        }
        emissions_per_stage = {
            'CO2': {}, 'Energy': {}, 'Water': {}
        }

        # Process emissions data
        for e in emissions:
            if e.emission_stage == Emissions.EmissionStage.CO2:
                total_emissions['CO2'] += e.total
                emissions_per_stage['CO2'] = {
                    'fibers': e.fibers,
                    'yarn_production': e.yarn_production,
                    'fabric_production': e.fabric_production,
                    'finishing': e.finishing,
                    'manufacturing': e.manufacturing,
                    'packaging': e.packaging,
                    'transport': e.transport,
                    'use': e.use,
                }
            elif e.emission_stage == Emissions.EmissionStage.ENERGY:
                total_emissions['Energy'] += e.total
                emissions_per_stage['Energy'] = {
                    'fibers': e.fibers,
                    'yarn_production': e.yarn_production,
                    'fabric_production': e.fabric_production,
                    'finishing': e.finishing,
                    'manufacturing': e.manufacturing,
                    'packaging': e.packaging,
                    'transport': e.transport,
                    'use': e.use,
                }
            elif e.emission_stage == Emissions.EmissionStage.WATER:
                total_emissions['Water'] += e.total
                emissions_per_stage['Water'] = {
                    'fibers': e.fibers,
                    'yarn_production': e.yarn_production,
                    'fabric_production': e.fabric_production,
                    'finishing': e.finishing,
                    'manufacturing': e.manufacturing,
                    'packaging': e.packaging,
                    'transport': e.transport,
                    'use': e.use,
                }

        # Adjust emissions and cost if the gown is reusable
        if obj.reusable and obj.washes > 0:
            total_emissions = {key: value / obj.washes for key, value in total_emissions.items()}
            for stage in emissions_per_stage:
                emissions_per_stage[stage] = {k: v / obj.washes for k, v in emissions_per_stage[stage].items()}

        return {
            'total_emissions': total_emissions,
            'emissions_per_stage': emissions_per_stage
        }


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
