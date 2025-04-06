import json
import pandas as pd
import os

# keydict = {
#     "modeloptions": ["emissions.gown", "emissions.emissions"],
#     "emissions.gown": ["name", "reusable", "cost", "weight", "washes", "comfort", "hygine"],
#     "emissions.emissions": ["fibers", "yarn_production", "fabric_production", "finishing", "manufacturing", "packaging", "transport", "use"]
# }

def get_gowns(loc=False):
    if not loc:
        location = r"emissions\data\AllDataVariables.csv"
    else:
        location = loc
    gowndf = pd.read_csv(location, header=0, sep=";")
    return gowndf


# Read the CSV data
data = get_gowns()
fixture = []
gown_pk_counter = 1
emission_pk_counter = 1

# Process each row
for idx, row in data.iterrows():
    # Create Gown entry
    gown_entry = {
        "model": "emissions.gown",
        "pk": gown_pk_counter,
        "fields": {
            "name": row["Gown"],
            "visible": True,  # Default value; change if needed
            "type": row["Type"],
            "reusable": row["Reusable"],
            "woven": row["Woven"],
            "cost": row["Price"],  # Convert to float-compatible format
            "laundry_cost": 1.25,  # Set to None or calculate if available
            "weight": row["Weight"],
            "fte_local": row["Local FTE"],
            # "fte_local_extra": 0,
            "washes": row["Longevity"],
            "comfort": 6,
            "hygine": 6,
            "waste_cost": 0,
            "residual_value": 0.03,
            "source": "Roel",  # Replace with a relevant value
        }
    }
    fixture.append(gown_entry)

    # Add Emissions entries
    for stage in ["Production", "Use", "Lost", "EOL"]:
        for substage, prefix in {
            "Total": "Total",
            "Raw": "Raw",
            "Advanced": "Advanced",
            "Transport": "Transport"
        }.items():
            # Check if the required columns exist in the row
            if f"{stage}-{prefix}-Cost" in row and f"{stage}-{prefix}-CO2" in row and f"{stage}-{prefix}-Energy" in row and f"{stage}-{prefix}-Water" in row:
                emission_entry = {
                    "model": "emissions.emissionsnew",
                    "pk": emission_pk_counter,
                    "fields": {
                        "gown": gown_pk_counter,
                        "emission_stage": stage,
                        "emission_substage": substage,
                        "cost": float(row[f"{stage}-{prefix}-Cost"]),
                        "co2": float(row[f"{stage}-{prefix}-CO2"]),
                        "energy": float(row[f"{stage}-{prefix}-Energy"]),
                        "water": float(row[f"{stage}-{prefix}-Water"]),
                        "recipe": row.get(f"{stage}-{prefix}-Recipe", None) if f"{stage}-{prefix}-Recipe" in row else None
                    }
                }
                fixture.append(emission_entry)
                emission_pk_counter += 1

    gown_pk_counter += 1

# Save the fixture to a JSON file
with open("data_list.json", "w") as final:
    json.dump(fixture, final, indent=4)


