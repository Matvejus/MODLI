from rest_framework import serializers
from .models import Gown, Emissions

class GownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gown
        fields = ['id', 'name', 'cost', 'washes', 'reusable']

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
