import json
import pandas as pd
import os

keydict = {
    "modeloptions": ["emissions.gown", "emissions.emissions"],
    "emissions.gown": ["name", "reusable", "cost", "weight", "washes", "comfort", "hygine"],
    "emissions.emissions": ["fibers", "yarn_production", "fabric_production", "finishing", "manufacturing", "packaging", "transport", "use"]
}

def get_gowns(loc=False):
    if not loc:
        location = ".\emissions\data\EverythingCombined.csv"
    else:
        location = loc
    gowndf = pd.read_csv(location, header=0, sep=";")
    return gowndf


# Read the CSV data
gdf = get_gowns()
lsts = []
pk_counter = 1  

# Process gowns
for idx, row in gdf.iterrows():
    gown_entry = {
        "model": "emissions.gown",
        "pk": idx + 1, 
        "fields": {
            "name": row["Gown"],
            "reusable": row["Reusable"], 
            "cost": row["Price"],
            "weight": row["Weight"],
            "washes": row["Longevity"],
            "comfort": row["Comfort"],
            "hygine": row["Hygiene"],
            "source": row["Main Source"]
        }
    }
    lsts.append(gown_entry)

    for emission_stage in ["Cost", "CO2", "Energy", "Water"]:
        emission_entry = {
            "model": "emissions.emissions",
            "pk": pk_counter,
            "fields": {
                "gown": idx + 1,
                "emission_stage": emission_stage,
                "production": row[f"Production-{emission_stage}"],
                "use": row[f"Use-{emission_stage}"],
                "lost": row[f"LOST-{emission_stage}"],
                "eol": row[f"EOL-{emission_stage}"],
                "fibers": 0,
                "yarn_production": 0,
                "fabric_production": 0,
                "finishing": 0,
                "packaging": 0,
                "transport": 0,
            }
        }
        lsts.append(emission_entry)
        pk_counter += 1
    
with open("test_list.json", "w") as final:
    json.dump(lsts, final, indent=4)

# print(json.dumps(lsts, indent=4))


