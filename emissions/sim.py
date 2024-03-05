from .models import Gown

def stock_emissions():
    reusable = Gown.objects.get(id = 1)
    disposable = Gown.objects.get(id = 2)
    reuse =[]
    disp = []
    for x in range(1,1001):
        use_nre = reusable.nre_emissions * x
        use_co2 = reusable.co2 * x
        use_blue_water = reusable.blue_water * x
        purchase_cost = 3*x
        washing_cost = 0.65*75*x
        res_coll = {'type': 'reusable',
                    'amount': x, 
                    'nre':use_nre,
                      'co2': use_co2,
                        'blue_water': use_blue_water,
                          'cost': purchase_cost,
                            'washing_cost': washing_cost,
                            'total_cost': washing_cost+purchase_cost}
        reuse.append(res_coll)

        disp_nre = disposable.nre_emissions * x
        disp_co2 = disposable.co2 * x
        disp_blue_water = disposable.blue_water * x
        purchase_cost = x
        disp_coll = {'type': 'disposable',
                    'amount': x, 
                    'nre':disp_nre,
                      'co2': disp_co2,
                        'blue_water': disp_blue_water,
                            'total_cost': purchase_cost}
        disp.append(disp_coll)

    return(reuse, disp)

    dicts

    [{'reusables': amount, 'disposable': amount, 
      'emissions':{'nre':reusable[nre]+disposable[nre],
                 'co2':reusalbe[co2]+disposable[co2],
                 'blue_water': reusable[blue_water]+disposable[blue_water]
                 },
        'washing_cost': reusable[washing_cost],
        'cost': reusable[total_cost]+disposable[total+cost]          
      }]
    

import json

def stock_emissions_to_json():
    reusable = Gown.objects.get(id=1)
    disposable = Gown.objects.get(id=2)
    emissions_data = []

    # Generate combinations of reusable and disposable items
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

    # Dump emissions_data to a JSON file
    with open('works.json', 'w') as json_file:
        json.dump(emissions_data, json_file, indent=4)




      

    


