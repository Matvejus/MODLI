from rest_framework import serializers
from .models import Gown, Certification, EmissionsNew


class EmissionImpactSerializer(serializers.Serializer):
    CO2 = serializers.FloatField()
    Energy = serializers.FloatField()
    Water = serializers.FloatField()
    Cost = serializers.FloatField()

class CertificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    class Meta:
        model = Certification
        fields = ['id', 'name', 'description']
        
class GownSerializer(serializers.ModelSerializer):
    emission_impacts = serializers.SerializerMethodField()
    certificates = CertificationSerializer(many=True)
    class Meta:
        model = Gown
        fields = ['id', 'name', 'cost', 'laundry_cost', 'residual_value', 'waste_cost', 'washes', 'reusable', 'fte_local', 'fte_local_extra',
                  'visible', 'comfort', 'hygine', 'certificates', 'emission_impacts',]
        
    def get_attribute_value(self, obj, attr):
        """Get attribute value from session data if available, otherwise from obj"""
        session_data = self.context.get('session_data', {})
        return session_data.get(attr, getattr(obj, attr))
        
    def get_emission_impacts(self, obj):
        emissions = EmissionsNew.objects.filter(gown=obj)
        
        # Use session values if available
        waste_cost = self.get_attribute_value(obj, 'waste_cost')
        residual_value = self.get_attribute_value(obj, 'residual_value')
        washes = self.get_attribute_value(obj, 'washes')
        reusable = self.get_attribute_value(obj, 'reusable')
        cost = self.get_attribute_value(obj, 'cost')

        total_emissions = {
            'purchase_cost': sum(float(e.cost) for e in emissions if e.cost is not None) + cost,
            'use_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'Use'),
            'lost_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'LOST'),
            'eol_cost': sum(float(e.cost) for e in emissions if e.emission_stage == 'EOL'),
            'waste': waste_cost if waste_cost is not None else 0,
            'residual_value': residual_value * 100 if residual_value is not None else 0,
        }

        # Pass session-modified obj to calculation methods
        total_emissions["CO2"] = self.calculate_total_emissions(emissions, 'co2', obj, washes)
        total_emissions["Energy"] = self.calculate_total_emissions(emissions, 'energy', obj, washes)
        total_emissions["Water"] = self.calculate_total_emissions(emissions, 'water', obj, washes)

        # Adjust emissions and cost if the gown is reusable
        if reusable and washes > 0 and any(key in ['purchase_cost', 'CO2', 'Energy', 'Water', 'residual_value'] for key in total_emissions):
            total_emissions = {key: value / washes for key, value in total_emissions.items()}

        return total_emissions
    
    def calculate_total_emissions(self, emissions, emission_type, obj, washes=None):
        # Use passed washes if provided, otherwise get from obj
        if washes is None:
            washes = self.get_attribute_value(obj, 'washes')
            
        return (
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_stage == 'Production' and e.emission_substage == 'Total') +
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_stage == "USE") * washes +
            sum(float(getattr(e, emission_type)) for e in emissions if e.emission_stage == "EOL")
        )



class GownDetailSerializer(serializers.ModelSerializer):
    certificates = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Certification.objects.all()
    )
    class Meta:
        model = Gown
        fields = ['name', 'reusable', 'cost', 'laundry_cost', 'residual_value', 'waste_cost', 'washes', 'comfort', 'hygine', 'certificates', 'fte_local', 'fte_local_extra']


class CertificationModel(serializers.ModelSerializer):

    class Meta:
        model = Certification
        fields  = '__all__'