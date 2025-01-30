from rest_framework import serializers
from .models import Gown, Emissions, Certification, EmissionsNew


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
        fields = ['id', 'name', 'cost', 'laundry_cost', 'residual_value', 'waste_cost', 'washes', 'reusable', 'fte_local', 'fte_local_extra',
                  'visible', 'comfort', 'hygine', 'certificates', 'emission_impacts',]

    def get_emission_impacts(self, obj):
        emissions = EmissionsNew.objects.filter(gown=obj)

        total_emissions = {
            'CO2': sum(float(e.co2) for e in emissions if e.co2 is not None ),
            'Energy': sum(float(e.energy) for e in emissions if e.energy is not None),
            'Water': sum(float(e.water) for e in emissions if e.water is not None),
            'purchase_cost': sum(float(e.cost) for e in emissions if e.cost is not None),
            # 'recipe': sum(float(e.recipe) for e in emissions if e.recipe is not None),
            # 'production_costs': sum(float(e.cost) for e in emissions if e.emission_stage == 'Production'),
            'use_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'Use'),
            'lost_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'LOST'),
            'eol_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'EOL'),
            'waste': obj.waste_cost if obj.waste_cost is not None else 0,
            'residual_value': obj.residual_value if obj.residual_value is not None else 0,
        }

        # Adjust emissions and cost if the gown is reusable
        if obj.reusable and obj.washes > 0 and any(key in ['purchase_cost', 'CO2', 'Energy', 'Water', 'residual_value'] for key in total_emissions):
            total_emissions = {key: value / obj.washes for key, value in total_emissions.items()}
        return total_emissions

class GownDetailSerializer(serializers.ModelSerializer):
    certificates = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Certification.objects.all()
    )
    class Meta:
        model = Gown
        fields = ['name', 'reusable', 'cost', 'laundry_cost', 'residual_value', 'waste_cost', 'washes', 'comfort', 'hygine', 'certificates', 'fte_local', 'fte_local_extra']

class EmissionSerializer(serializers.ModelSerializer):
    gown = serializers.StringRelatedField()
    class Meta:
        model = Emissions
        fields = ['gown', 'emission_stage', 'fibers', 'yarn_production', 'fabric_production', 'finishing', 'production', 'packaging', 'transport', 'use', 'total']
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'description']