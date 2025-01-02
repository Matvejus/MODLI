import json
import pandas as pd

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
            "reusable": row["Reusable"] == "TRUE", 
            "cost": row["Price"],
            "weight": row["Weight"],
            "washes": row["Longevity"],
            "comfort": row["Comfort"],
            "hygine": row["Hygiene"]
        }
    }
    lsts.append(gown_entry)

    for emission_stage in ["COST", "CO2", "ENERGY", "WATER"]:
        emission_entry = {
            "model": "emissions.emissions",
            "pk": pk_counter,
            "fields": {
                "gown": idx + 1,
                "emission_stage": emission_stage,
                "fibers": row[f"Production-{emission_stage}"],
                "yarn_production": row[f"Use-{emission_stage}"],
                "fabric_production": row[f"LOST-{emission_stage}"],
                "finishing": row[f"EOL-{emission_stage}"]
            }
        }
        lsts.append(emission_entry)
        pk_counter += 1

with open("test_list.json", "w") as final:
    json.dump(lsts, final, indent=4)


