from django.shortcuts import render, get_object_or_404, redirect
from .models import Gown, Emissions
from .forms import GownForm, GownSelectionForm, GownFormReusable
import json
from django.core import serializers

def needed_amount(amount):
    with open('emissions\data\works.json', 'r') as file:
        data = json.load(file)

    amount = int(amount)
    combinations = [combo for combo in data if combo['total'] == amount]
    
    return combinations

def cheapest(combinations):
    min_price = min(c['cost'] for c in combinations)
    cheapest = [c for c in combinations if c['cost'] == min_price]

    return cheapest

def lowest_emissions(combinations):
    min_emissions = min(c['total_emissions'] for c in combinations)
    lowest_emissions = [c for c in combinations if c['total_emissions'] == min_emissions]

    return lowest_emissions

def optimal(combinations):
    best_combo = float('inf')
    best = None

    for c in combinations:
        total = c['cost'] + c['total_emissions']
        if total < best_combo:
            best = c
            best_combo = total

    return best
    




def calculator(request):
    context = {}  # Define the context variable here

    if request.method == 'POST':
        return render(request, 'calculator.html', context)

    return render(request, 'calculator.html')


def gown_list(request):
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
                gown_weight_kg = gown.weight / 1000  # Convert grams to kilograms
                
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



