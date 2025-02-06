import json
import logging
import traceback

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Gown, Emissions, Certification
from .OPT import GownOptimizer
from .serializers import GownSerializer, GownDetailSerializer, EmissionSerializer, CertificationSerializer



@api_view(['GET'])
def gown_list(request):
    gowns = Gown.objects.all()
    serializer = GownSerializer(gowns, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def selected_gowns_emissions(request):
    gown_ids = request.GET.get('ids', '').split(',')
    gowns = Gown.objects.filter(id__in=gown_ids)
    serializer = GownSerializer(gowns, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
def gown_detail(request, pk):
    try:
        gown = Gown.objects.get(pk=pk)
    except Gown.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = GownDetailSerializer(gown)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GownDetailSerializer(gown, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def gown_emissions(request, pk):
    emissions = Emissions.objects.filter(gown_id=pk)
    serializer = EmissionSerializer(emissions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def optimize_gowns_api(request):
    try:
        # Parse the JSON data from the request
        data = json.loads(request.body)
        
        # Extract gowns and specifications from the request data
        gown_data = data.get('gowns', [])
        specifications = data.get('specifications', {})

        # Validate input data
        if not gown_data or not specifications:
            return Response({'error': 'Invalid input data. Both gowns and specifications are required.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Create and run the optimizer
        optimizer = GownOptimizer(gown_data, specifications)
        results = optimizer.optimize()
        # Return the results as JSON response
        return Response({'results': results}, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Optimization error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# class GownEmissionsAPIView(APIView):
#     def get(self, request):
#         gowns_data = []
#         gowns = Gown.objects.all()
        
#         for gown in gowns:
#             emissions = Emissions.objects.filter(gown=gown)
#             total_co2 = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.CO2)
#             total_energy = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.ENERGY)
#             total_water = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.WATER)
#             cost = gown.cost

#             gowns_data.append({
#                 "gown": gown.id,
#                 "name": gown.name,
#                 "reusable": gown.reusable,
#                 "emissions": {
#                     "CO2": total_co2,
#                     "Energy": total_energy,
#                     "Water": total_water,
#                     "Cost": cost,
#                 }
#             })
#         return Response(gowns_data)

@api_view(['GET'])
def all_certificates(request):
    certificates = Certification.objects.all()
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data)

class CertificationView(APIView):
    def post(self, request, format=None):
        serializer = CertificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            certification = Certification.objects.get(pk=pk)
        except Certification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CertificationSerializer(certification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            certification = Certification.objects.get(pk=pk)
        except Certification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        certification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)