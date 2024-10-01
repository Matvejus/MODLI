import pyscipopt as ps
from pyscipopt import quicksum
import json
from gurobipy import GRB
from enum import Enum
import itertools
import os

os.chdir('./emissions/')

class Envpar(Enum):
    CO2EQ = 1
    WATER = 2
    ENERGY = 3
    MONEY = 4

class Stages(Enum):
    HOSPITAL = 1
    LAUNDRY = 2
    USAGE = 3
    LOST = 4
    EOL = 5
    ARRIVALMOM = 6
    NEWARRIVALS = 7

#Stages where impact is made per gown
Accountables = [Stages.NEWARRIVALS, Stages.LAUNDRY, Stages.LOST, Stages.EOL,Stages.ARRIVALMOM]

#A large value that caps how many gowns can be bought at once per type.
LARGEVALUE = 10000

class Gown:
    def __init__(self, name, reusable, impacts):
        self.Name = name
        self.Reusable = reusable
        self.Impacts = impacts

class Specs:
    def __init__(self, usage_per_week, pickups_per_week,optimizer=[Envpar.MONEY]):
        self.usage_per_week = usage_per_week
        self.pickups_per_week = pickups_per_week
        self.usage_between_pickup = self.usage_per_week / self.pickups_per_week
        self.optimizer = optimizer

#Creates cartesian product of all lists entered if multiple are given in *lsts. 
#If only one list is given, just returns that list.
def varsList(*lsts):
    if len(lsts)>1:
        retlist = list(itertools.product(*lsts))
    else:
        retlist = lsts[0]
    return retlist

#For a list of keys, adds a variable of type vtype.
def addVars(varlist,vtype):
    dct = {}
    for x in varlist:
        dct[x] = md.addVar(vtype=vtype,name=str(x))
    return dct

#Retrieves gowns.
def get_gowns(loc=False):
    if loc == False:
        location = "../Data/MockGowns1.json"
    else:
        location = loc
    
    f = open(location)
    _options = json.load(f)
    print(_options)
    Options = [Gown(name = gw["name"], reusable = gw["reusable"], impacts = gw["impacts"]) for gw in _options]
    return Options
    
#Retrieves impact-factors for a given gown, Stage and Environmental-factor.
def get_impact(gown, stage, env):
    if stage not in Accountables:
        return 0
    else:
        yvar = gown.Impacts["envpars"].index(env.name)
        xvar = gown.Impacts["stages"].index(stage.name)
        return gown.Impacts["params"][xvar][yvar]

#Get all gowns and specifications for the system
Options = get_gowns()
Specifications = Specs(usage_per_week=1000, pickups_per_week=2)

# Timesteps = input from the dashboard
timesteps = 150
Time = range(timesteps)

#Create Model
md = ps.Model("gown_optimization")

#Create environmental cost vars
def make_cost_vars(Options):
    total_impacts = {}
    partial_impacts = {}
    var_list = varsList(Stages,Envpar,Time)
    
    for x in Options:
        print("Reusable:", x.Reusable)
        total_impacts[x] = addVars(Envpar, vtype="C")
        partial_impacts[x] = addVars(var_list, vtype="C")

    cost_vars = {"TOTAL": total_impacts, "PARTIAL" : partial_impacts}
    return cost_vars

#Create decision variables
def make_decision_vars(options):
    options_time = varsList(options,Time)
    dct_var = {}
    dct_var[Stages.ARRIVALMOM] = addVars(options_time, vtype="B")
    dct_var[Stages.NEWARRIVALS] = addVars(options_time, vtype="I")
    dct_var[Stages.HOSPITAL] = addVars(options_time, vtype="I")
    dct_var[Stages.LAUNDRY] = addVars(options_time, vtype="I")
    dct_var[Stages.EOL] = addVars(options_time, vtype="I")
    dct_var[Stages.LOST] = addVars(options_time, vtype="I")
    dct_var[Stages.USAGE] = addVars(options_time, vtype="I")
    return dct_var


# Initialize the hospital gowns at time 0
def initial_settings(Options,dv,initial_gowns=500, md=md):
    for ix,x in enumerate(Options):
        if isinstance(initial_gowns,int):
            md.addCons(dv[Stages.HOSPITAL][x, 0] == initial_gowns, name=f"initial_gowns_{x.Name}")
        elif isinstance(initial_gowns,list):
            md.addCons(dv[Stages.HOSPITAL][x, 0] == initial_gowns[ix], name=f"initial_gowns_{x.Name}")
        else:
            print("Error in initialization")
        md.addCons(dv[Stages.LAUNDRY][x,0]==0)
        md.addCons(dv[Stages.EOL][x,0]==0)
        md.addCons(dv[Stages.LOST][x,0]==0)
    return md

# Constraints to manage the flow of gowns
def gown_flow(dv, md=md):
    for t in Time[:-1]:
        for x in Options:
            md.addCons(dv[Stages.HOSPITAL][x, t + 1] == dv[Stages.HOSPITAL][x, t] - dv[Stages.USAGE][x, t] + dv[Stages.LAUNDRY][x, t] + dv[Stages.NEWARRIVALS][x, t], name=f"HOSPITAL_balance_{x.Name}_{t}")
            md.addCons(dv[Stages.USAGE][x, t] == dv[Stages.LOST][x, t + 1] + dv[Stages.LAUNDRY][x, t + 1] + dv[Stages.EOL][x, t + 1], name=f"USAGE_balance_{x.Name}_{t}")
            md.addCons(dv[Stages.USAGE][x, t] <= dv[Stages.HOSPITAL][x, t], name=f"USAGE_limit_{x.Name}_{t}")
            md.addCons(dv[Stages.LAUNDRY][x, t + 1] <= dv[Stages.USAGE][x, t] * x.Reusable, name=f"LAUNDRY_limit_{x.Name}_{t}")
            md.addCons(dv[Stages.NEWARRIVALS][x,t] <= dv[Stages.ARRIVALMOM][x,t]*LARGEVALUE)
    for t in Time:
        md.addCons(quicksum(dv[Stages.USAGE][x, t] for x in Options) == Specifications.usage_between_pickup, name=f"USAGE_total_{t}")
    return md

# Calculate environmental impact for all parameters
def calculate_costs(dv, cv, md = md):
    total_impacts = cv["TOTAL"]
    partial_impacts = cv["PARTIAL"]
    for cs,st,x,t in varsList(Envpar,Stages,Options,Time):
        md.addCons(partial_impacts[x][st,cs,t] == dv[st][x,t]*get_impact(x,st,cs))
    for cs,x in varsList(Envpar,Options):
        md.addCons(total_impacts[x][cs] == quicksum(partial_impacts[x][st,cs,t] for st in Stages for t in Time))

    return md

# Balance usage of usable/reusable
def balance_reusable(dv,mn,mx, md = md):
    if mn > 1 or (mx < mn):
        mn = 0.1
        mx = 0.9


    md.addCons(quicksum(dv[Stages.USAGE][x, t] for t in Time for x in Options if x.Reusable) >= 
               mn * quicksum(dv[Stages.USAGE][x,t] for t in Time for x in Options), name=f"BALANCE_reusable")
    md.addCons(quicksum(dv[Stages.USAGE][x, t] for t in Time for x in Options if x.Reusable) <= 
               mx * quicksum(dv[Stages.USAGE][x,t] for t in Time for x in Options), name=f"BALANCE_disposable")
        
    return md

#Make decision and cost-variables
dv = make_decision_vars(Options)
cv = make_cost_vars(Options)

#Set the constraints.
#First, fix the number of gowns at the hospital at time 0; default is 50 gowns per type.
#Add the constraints that manage the gown flow: LAUNDRY, USAGE, LOST, EOL, etcetera.
#Calculate the cost and add them as constraints for the cost-variables. 
#Give a window of what percentage of the gowns used should be reusable; default between 10-90%.
md = initial_settings(Options,dv,[2000,0,0])
md = gown_flow(dv)
md = calculate_costs(dv,cv)
md = balance_reusable(dv,0.2,0.7)

# Set objective to minimize all environmental impacts and costs
md.setObjective(quicksum(cv["TOTAL"][x][cs] for cs in Specifications.optimizer for x in Options),'minimize')

# Optimize the model
md.optimize()

# Check if the model is optimized successfully
if md.getStatus() != "optimal":
    print("Model is infeasible. Analyzing infeasibilities...")
    md.computeIIS()
    md.write("model.ilp")
    for c in md.getConstrs():
        if c.IISConstr:
            print(f"Infeasible constraint: {c.constrName}")
elif md.getStatus() == "optimal":
    print("Results of gown usage for each variant:")
    for x in Options:
        usage_values = [int(md.getVal(dv[Stages.USAGE][x, t])) for t in Time]
        new_arrivals = [(x,int(y)) for (x,y) in [(t,md.getVal(dv[Stages.NEWARRIVALS][x,t])) for t in Time] if y > 0]
        total_impact = cv["TOTAL"]
        print(f"Gown '{x.Name}' with impacts {x.Impacts}:")
        print(f"Usage values: {usage_values}\n")
        print(f"Arrivals (time,amount): {new_arrivals}\n")
        print("Total impacts:")
        for cs in Envpar:
            print(f"{cs.name}: {md.getVal(total_impact[x][cs])}")
else:
    print("Optimization was not successful. Status code:", md.getStatus())

# Identify the best option based on the total costs and impacts
#best_option = min(Options, key=lambda x: sum(md.getVal(cv["TOTAL"][x][cs]) for cs in Envpar))
#print(f"The best option is the gown '{best_option.Name}' with impacts {best_option.Impacts}.")
