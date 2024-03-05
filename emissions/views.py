from django.shortcuts import render
from .models import Gown
import json


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
    best =[]

    for c in combinations:
        total = c['cost']+c['total_emissions']
        if total < best_combo:
            best.append(total)
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
