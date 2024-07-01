from django.shortcuts import render, get_object_or_404, redirect
from .models import Gown
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
        amount = request.POST.get('amount')
        lowest_cost_value = request.POST.get('lowest_cost')
        lowest_emissions_value = request.POST.get('lowest_emissions')

        lowest_emissions_boolean = lowest_emissions_value == 'on'
        lowest_cost_boolean = lowest_cost_value == 'on'

        if amount:
            gowns = needed_amount(amount)
            
            if lowest_cost_boolean:
                lowest_cost = cheapest(gowns)
                context = {'gowns': lowest_cost}
                return render(request, 'calculator.html', context)
            
            elif lowest_emissions_boolean:
                emissions = lowest_emissions(gowns)
                context = {'gowns': emissions}
                return render(request, 'calculator.html', context)
            
            elif lowest_cost_boolean and lowest_emissions_boolean:
                best_combination = optimal(gowns)
                context = {'gowns': best_combination}
                return render(request, 'calculator.html', context)

    return render(request, 'calculator.html')


def gown_list(request):
    reusable_gowns = Gown.objects.filter(reusable=True)
    single_use_gowns = Gown.objects.filter(reusable=False)

    if request.method == 'POST':
        form = GownSelectionForm(request.POST)
        if form.is_valid():
            selected_gowns = form.cleaned_data['selected_gowns']
            serialized_gowns = serializers.serialize('json', selected_gowns)
            context = {'serialized_gowns': serialized_gowns, "selected_gowns": selected_gowns}
            return render(request, 'selected_gowns.html', context)
    else:
        form = GownSelectionForm()

    return render(request, 'entrypage.html', {
        'reusable_gowns': reusable_gowns,
        'single_use_gowns': single_use_gowns,
        'form': form
    })

def compare(request):
    return render(request, 'selected_gowns.html')


# def gown_list(request):
#     reusable_gowns = Gown.objects.filter(reusable=True)
#     single_use_gowns = Gown.objects.filter(reusable=False)

#     if request.method == 'POST':
#         form = GownSelectionForm(request.POST)
#         if form.is_valid():
#             selected_gowns = form.cleaned_data['selected_gowns']
#             return render(request, 'selected_gowns.html', {'selected_gowns': selected_gowns})
#     else:
#         form = GownSelectionForm()

#     return render(request, 'entrypage.html', {
#         'reusable_gowns': reusable_gowns,
#         'single_use_gowns': single_use_gowns,
#         'form': form
#     })

# def compare(request):
#     return render(request, 'selected_gowns.html')


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



