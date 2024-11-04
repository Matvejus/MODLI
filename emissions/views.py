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

from .forms import GownForm, GownSelectionForm, GownFormReusable
from .models import Gown, Emissions
from .OPT import GownOptimizer
from .serializers import GownSerializer, GownDetailSerializer, EmissionSerializer

logger = logging.getLogger(__name__)

def calculator(request):
    context = {}  # Define the context variable here

    if request.method == 'POST':
        return render(request, 'calculator.html', context)

    return render(request, 'calculator.html')


def gowns(request):
    reusable_gowns = Gown.objects.filter(reusable=True)
    single_use_gowns = Gown.objects.filter(reusable=False)

    if request.method == 'POST':
        return compare(request)

    else:
        form = GownSelectionForm()

    return render(request, 'entrypage.html', {
        'reusable_gowns': reusable_gowns,
        'single_use_gowns': single_use_gowns,
        'form': form
    })

def compare(request):
    if request.method == 'POST':
        form = GownSelectionForm(request.POST)
        if form.is_valid():
            selected_gowns = form.cleaned_data['selected_gowns']
            emissions_data = Emissions.objects.filter(gown__in=selected_gowns)
            
            # Process all emissions data by dividing by gown weight in kg and formatting to 2 decimal places
            normalized_emissions = []
            for emission in emissions_data:
                gown = emission.gown
                gown_weight_kg = gown.weight / 1000 # Convert grams to kilograms * AMOUNTS OF GOWNS to calc emissions
                
                normalized_emission = {
                    'gown_id': gown.id,
                    'emission_stage': emission.emission_stage,
                    'fibers': round(emission.fibers * gown_weight_kg, 2),
                    'yarn_production': round(emission.yarn_production * gown_weight_kg, 2),
                    'fabric_production': round(emission.fabric_production * gown_weight_kg, 2),
                    'finishing': round(emission.finishing * gown_weight_kg, 2),
                    'manufacturing': round(emission.manufacturing * gown_weight_kg, 2),
                    'packaging': round(emission.packaging * gown_weight_kg, 2),
                    'transport': round(emission.transport * gown_weight_kg, 2),
                    'use': round(emission.use * gown_weight_kg, 2),
                }
                normalized_emissions.append(normalized_emission)

            # Create dictionaries for each emission type
            co2_emissions_dict = {}
            energy_emissions_dict = {}
            water_emissions_dict = {}

            # Organize the normalized emissions into dictionaries by emission type
            for norm_emission in normalized_emissions:
                gown_id = norm_emission['gown_id']
                if norm_emission['emission_stage'] == Emissions.EmissionStage.CO2:
                    co2_emissions_dict[gown_id] = norm_emission
                elif norm_emission['emission_stage'] == Emissions.EmissionStage.ENERGY:
                    energy_emissions_dict[gown_id] = norm_emission
                elif norm_emission['emission_stage'] == Emissions.EmissionStage.WATER:
                    water_emissions_dict[gown_id] = norm_emission

            serialized_gowns = serializers.serialize('json', selected_gowns)
            serialized_emissions = serializers.serialize('json', emissions_data)
            
            context = {
                'serialized_gowns': serialized_gowns,
                'serialized_emissions': serialized_emissions,
                'selected_gowns': selected_gowns,
                'co2_emissions_dict': co2_emissions_dict,
                'energy_emissions_dict': energy_emissions_dict,
                'water_emissions_dict': water_emissions_dict,
            }
            return render(request, 'selected_gowns.html', context)

        # If the form is not valid, handle it (e.g., redirect or return an error)
        return redirect('entrypage')

    # Handle the case when the request method is not POST, possibly redirect or return an error
    return render(request, 'entrypage.html', {
        'error': 'Invalid request method. Please use the form to select gowns.',
    })


def gown_edit(request, id):
    gown = get_object_or_404(Gown, id=id)
    if request.method == 'POST':
        if gown.reusable:
            form = GownFormReusable(request.POST, instance=gown)
        else:
            form = GownForm(request.POST, instance=gown)

        if form.is_valid():
            form.save()
            return redirect('gown_list')

    else:
        if gown.reusable:
            form = GownFormReusable(instance=gown)
        else:
            form = GownForm(instance=gown)


    context = {
        'form':form,
        'gown': gown
    }
    return render(request, 'gown_edit.html', context)

def scenario1(request):
    value = 2
    context = {
        "data":value
    }
    return render(request, 'emissions.html', context )


@api_view(['GET'])
def gown_list(request):
    gowns = Gown.objects.all()
    serializer = GownSerializer(gowns, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def gown_detail(request, pk):
    try:
        gown = Gown.objects.get(pk=pk)
    except Gown.DoesNotExist:
        return Response(status=404)

    serializer = GownDetailSerializer(gown)
    return Response(serializer.data)

@api_view(['GET'])
def gown_emissions(request, pk):
    emissions = Emissions.objects.filter(gown_id=pk)
    serializer = EmissionSerializer(emissions, many=True)
    return Response(serializer.data)



def read_mock_gowns():
    with open('C:\DEV\Programms\modli_py\emissions\data\MockGowns.json', 'r') as file:
        return json.load(file)

def optimize_gowns(request):
    if request.method == 'POST':
        try:
            # Read mock gowns data
            gown_data = read_mock_gowns()

            # Hardcoded specifications
            specifications = {
                "usage_per_week": 1400,
                "pickups_per_week": 2,
                "optimizer": ["MONEY"],
                "loss_percentage": 0.001
            }


            # Create and run the optimizer
            optimizer = GownOptimizer(gown_data, specifications)
            results = optimizer.optimize()

            return render(request, 'optimize_test.html', {'results': results})

        except Exception as e:
            logger.exception(f"Error in optimize_gowns: {str(e)}")
            error_message = f'Optimization error: {str(e)}'
            return render(request, 'optimize_test.html', {'error': error_message})
    
    # If it's a GET request, just render the form
    return render(request, 'optimize_test.html')


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

        print(results)
        # Return the results as JSON response
        return Response({'results': results}, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Error in optimize_gowns_api: {str(e)}")
        return Response({'error': f'Optimization error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class GownEmissionsAPIView(APIView):
    def get(self, request):
        gowns_data = []
        gowns = Gown.objects.all()
        
        for gown in gowns:
            emissions = Emissions.objects.filter(gown=gown)
            total_co2 = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.CO2)
            total_energy = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.ENERGY)
            total_water = sum(emission.total for emission in emissions if emission.emission_stage == Emissions.EmissionStage.WATER)
            cost = gown.cost

            gowns_data.append({
                "gown": gown.id,
                "name": gown.name,
                "reusable": gown.reusable,
                "emissions": {
                    "CO2": total_co2,
                    "Energy": total_energy,
                    "Water": total_water,
                    "Cost": cost,
                }
            })
        return Response(gowns_data)

    
def gown_emissions_view(request):
    # Create an instance of the API view
    api_view = GownEmissionsAPIView.as_view()
    
    # Call the API view to get the response
    response = api_view(request)
    
    # Extract the data from the response
    gowns_data = response.data
    
    # Render the template with the data
    return render(request, 'gown_emissions.html', {'gowns': gowns_data})
