from rest_framework import serializers
from .models import Gown, Certification, EmissionsNew


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
            'CO2': sum(e.co2 for e in emissions if e.co2 is not None ),
            'Energy': sum(e.energy for e in emissions if e.energy is not None),
            'Water': sum(e.water for e in emissions if e.water is not None),
            'purchase_cost': sum(e.cost for e in emissions if e.cost is not None),
            'recipe': sum(e.recipe for e in emissions if e.recipe is not None),
            # 'production_costs': sum(float(e.cost) for e in emissions if e.emission_stage == 'Production'),
            'use_cost': sum(e.cost for e in emissions if e.emission_stage == 'Use'),
            'lost_cost': sum(e.cost for e in emissions if e.emission_stage == 'LOST'),
            'eol_cost': sum(e.cost for e in emissions if e.emission_stage == 'EOL'),
            'waste': obj.waste_cost if obj.waste_cost is not None else 0,
            'residual_value': obj.residual_value * 100 if obj.residual_value is not None else 0,
        }

        total_emissions["CO2"] = self.calculate_total_emissions(emissions, 'co2', obj)
        # Calculate total emissions for Energy
        total_emissions["Energy"] = self.calculate_total_emissions(emissions, 'energy', obj)
        # Calculate total emissions for Water
        total_emissions["Water"] = self.calculate_total_emissions(emissions, 'water', obj)

        # Adjust emissions and cost if the gown is reusable
        if obj.reusable and obj.washes > 0 and any(key in ['purchase_cost', 'CO2', 'Energy', 'Water', 'residual_value'] for key in total_emissions):
            total_emissions = {key: value / obj.washes for key, value in total_emissions.items()}

        return total_emissions
    
    def calculate_total_emissions(self, emissions, emission_type, obj):
        return (
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_stage == 'Production' and e.emission_substage == 'Total') +
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_substage == "USE") * obj.washes -
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_substage == "EOL")
        )



class GownDetailSerializer(serializers.ModelSerializer):
    certificates = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Certification.objects.all()
    )
    class Meta:
        model = Gown
        fields = ['name', 'reusable', 'cost', 'laundry_cost', 'residual_value', 'waste_cost', 'washes', 'comfort', 'hygine', 'certificates', 'fte_local', 'fte_local_extra']

# class EmissionSerializer(serializers.ModelSerializer):
#     gown = serializers.StringRelatedField()
#     class Meta:
#         model = Emissions
#         fields = ['gown', 'emission_stage', 'fibers', 'yarn_production', 'fabric_production', 'finishing', 'production', 'packaging', 'transport', 'use', 'total']
class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'description']
