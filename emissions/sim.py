from .models import Gown
import json

def stock_emissions_to_json():
    reusable = Gown.objects.get(id=1)
    disposable = Gown.objects.get(id=2)
    emissions_data = []

    for amount_reusable in range(1, 1001):
        for amount_disposable in range(1, 1001):
            emissions = {
                'nre': round(reusable.nre_emissions * amount_reusable + disposable.nre_emissions * amount_disposable,2),
                'co2': round(reusable.co2 * amount_reusable + disposable.co2 * amount_disposable, 2),
                'blue_water': round(reusable.blue_water * amount_reusable + disposable.blue_water * amount_disposable, 2),
                'solid_waste': round(reusable.solid_waste* amount_reusable + disposable.solid_waste*amount_disposable, 2),
            }
            washing_cost = 0.65 * 75 * amount_reusable
            purchase_cost = 3 * amount_reusable + amount_disposable
            total_cost = washing_cost + purchase_cost
            total_emissions = round((reusable.nre_emissions * amount_reusable) + (disposable.nre_emissions * amount_disposable) +
                                (reusable.co2 * amount_reusable) + (disposable.co2 * amount_disposable) +
                                (reusable.blue_water * amount_reusable) + (disposable.blue_water * amount_disposable) +
                                (reusable.solid_waste* amount_reusable + disposable.solid_waste*amount_disposable)
                                , 2)

            data_entry = {
                'total': amount_disposable + amount_reusable,
                'reusables': amount_reusable,
                'disposable': amount_disposable,
                'emissions': emissions,
                'washing_cost': washing_cost,
                'cost': total_cost,
                'total_emissions': total_emissions,
            }
            emissions_data.append(data_entry)
            
    with open('emissions\data\works.json', 'w') as json_file:
        json.dump(emissions_data, json_file, indent=4)

    # Dump emissions_data to a JSON file






      

    


