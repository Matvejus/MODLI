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


from .models import Gown, Certification, EmissionsNew
from .OPT import GownOptimizer
from .serializers import GownSerializer, GownDetailSerializer, CertificationSerializer



@api_view(['GET'])
def gown_list(request):
    

    gowns = Gown.objects.all()
    serializer = GownSerializer(gowns, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def selected_gowns_emissions(request):
    print(request.session.session_key)
    gown_ids = request.GET.get('ids', '').split(',')
    result = []
    
    # Debug: print all session keys
    
    for gown_id in gown_ids:
        if not gown_id:
            continue
            
        gown_session_key = f"gown_{gown_id}"
        if gown_session_key in request.session:
            # Use the session data for this gown
            gown_data = request.session[gown_session_key]
            gown_data['id'] = gown_id
            
            try:
                # Get the gown object
                gown = Gown.objects.get(id=gown_id)
                
                # Use the serializer to get emissions data
                serializer = GownSerializer(gown)
                
                # Add the emission impacts to the gown data
                gown_data['emission_impacts'] = serializer.data['emission_impacts']
                
                result.append(gown_data)
            except Gown.DoesNotExist:
                # Handle case when gown doesn't exist
                gown_data['emission_impacts'] = None
                result.append(gown_data)
        else:
            # Use database data if no session data exists
            try:
                gown = Gown.objects.get(id=gown_id)
                serializer = GownSerializer(gown)
                result.append(serializer.data)
            except Gown.DoesNotExist:
                print(f"Gown {gown_id} not found in database")
                # Skip non-existent gowns
                pass
    
    return Response(result)


@api_view(['GET', 'POST'])
def gown_detail(request, pk):
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    # Define a session key for this specific gown
    gown_session_key = f"gown_{pk}"
    
    try:
        # Get the base gown data from the database
        base_gown = Gown.objects.get(pk=pk)
        
        # Check if we have session-specific data for this gown
        if gown_session_key in request.session:
            # Use session data but keep the database ID
            gown_data = request.session[gown_session_key]
            gown_data['id'] = base_gown.id
        else:
            # Initialize session with data from the database
            serializer = GownDetailSerializer(base_gown)
            request.session[gown_session_key] = serializer.data
            gown_data = serializer.data
            
    except Gown.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(gown_data)
    
    elif request.method == 'POST':
        serializer = GownDetailSerializer(data=request.data)
        if serializer.is_valid():
            # Save the updated data to the session, not the database
            request.session[gown_session_key] = serializer.validated_data
            request.session.modified = True  # Mark the session as modified
            
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def gown_emissions(request, pk):
    emissions = EmissionsNew.objects.filter(gown_id=pk)
    serializer = GownSerializer(emissions, many=True)
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