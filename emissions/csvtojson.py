import json
import pandas as pd
from enum import Enum
import os

keydict = {}
keydict["modeloptions"] = ["emissions.gown","emissions.emissions"]
keydict["emissions.gown"] = ["ID","Gown","Reusable","Weight","Longevity","Main Source","Price","Comfort","Hygiene"]
keydict["emissions.stages"] = ["Production","Use","LOST","EOL"]
keydict["emissions.emissions"] = ["Cost","CO2","Energy","Water"]

def get_gowns(loc=False):
    if loc == False:
        location = ".\emissions\data\EverythingCombined.csv"
    else:
        location = loc
    gowndf = pd.read_csv(location, header=0, sep=";")
    return gowndf

gdf = get_gowns()
lsts = []


for idx, row in gdf.iterrows():
    for mo in keydict["modeloptions"]:
        dct = {}
        dct["model"] = mo
        dct["fields"] = {}
        dct["ID"] = row["ID"]
        if mo == "emissions.gown":
            fields = keydict[mo]
            for f in fields:
                dct["fields"][f] = row[f]
            lsts.append(dct)
        elif mo == "emissions.emissions":
            fields = keydict[mo]
            for f in fields:
                dct["fields"] = {}
                for s in keydict["emissions.stages"]: 
                    dct["fields"]["emission.parameter"] = f
                    dct["fields"][s] = row[s+"-"+f]
                lsts.append(dct.copy())

print(lsts)

with open("newlist.json", "w") as final:
	json.dump(lsts, final)