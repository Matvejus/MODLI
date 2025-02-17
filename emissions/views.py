import json
import logging
import traceback
import jwt

from django.conf import settings

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import logging
logger = logging.getLogger(__name__)

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

def get_token_from_request(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def decode_token(token):
    try:    
        print(token)
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

@api_view(['GET', 'PUT'])
def gown_detail(request, pk):
    token = get_token_from_request(request)
    if not token:
        return Response({"error": "No token provided"}, status=401)

    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid or expired token"}, status=401)

    session_key = f"user_{payload.get('sub')}_gown_{pk}"

    if request.method == 'GET':
        # Check if modified data exists in the session
        gown_data = request.session.get(session_key)
        if gown_data:
            return Response(gown_data)

        # Otherwise, fetch the gown from DB
        try:
            gown = Gown.objects.get(pk=pk)
            serializer = GownDetailSerializer(gown)
            return Response(serializer.data)
        except Gown.DoesNotExist:
            return Response({"error": "Gown not found"}, status=404)

    elif request.method == 'PUT':
        serializer = GownDetailSerializer(data=request.data)
        if serializer.is_valid():
            request.session[session_key] = serializer.data
            request.session.modified = True
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_gown_session(request, gown_id):
    token = get_token_from_request(request)
    if not token:
        return Response({"error": "No token provided"}, status=401)

    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid or expired token"}, status=401)

    session_key = f"user_{payload.get('sub')}_gown_{gown_id}"
    gown_data = request.session.get(session_key)

    if gown_data:
        return Response(gown_data, status=200)
    
    try:
        gown = Gown.objects.get(pk=gown_id)
        serializer = GownDetailSerializer(gown)
        gown_data = serializer.data
        request.session[session_key] = gown_data
        request.session.modified = True
        return Response(gown_data, status=200)
    except Gown.DoesNotExist:
        return Response({"error": "Gown not found"}, status=404)

@api_view(['POST'])
def save_gown_session(request, gown_id):
    token = get_token_from_request(request)
    if not token:
        return Response({"error": "No token provided"}, status=401)

    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid or expired token"}, status=401)

    session_key = f"user_{payload.get('sub')}_gown_{gown_id}"
    request.session[session_key] = request.data
    request.session.modified = True

    return Response({"message": "Gown data saved in session"}, status=200)

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