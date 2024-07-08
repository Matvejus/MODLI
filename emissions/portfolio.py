import gurobipy as gp
import json
from gurobipy import GRB
from enum import Enum

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

Accountables = [Stages.NEWARRIVALS, Stages.LAUNDRY, Stages.LOST, Stages.EOL]

class Gown:
    def __init__(self, name, reusable, impacts):
        self.Name = name
        self.Reusable = reusable
        self.Impacts = impacts

class Specs:
    def __init__(self, usage_per_week, pickups_per_week, optimizer=[Envpar.MONEY]):
        self.usage_per_week = usage_per_week
        self.pickups_per_week = pickups_per_week
        self.usage_between_pickup = self.usage_per_week / self.pickups_per_week
        self.optimizer = optimizer

def get_gowns(loc=False):
    location = "../Data/MockGowns1.json" if not loc else loc
    
    with open(location) as f:
        _options = json.load(f)
    
    print(_options)
    Options = [Gown(name=gw["name"], reusable=gw["reusable"], impacts=gw["impacts"]) for gw in _options]
    return Options

def get_impact(gown, stage, env):
    if stage not in Accountables:
        stage = Accountables[0]
    yvar = gown.Impacts["envpars"].index(env.name)
    xvar = gown.Impacts["stages"].index(stage.name)
    return gown.Impacts["params"][xvar][yvar]

Options = get_gowns()
Specifications = Specs(usage_per_week=100, pickups_per_week=2)
print(get_impact(Options[1], stage=Stages.NEWARRIVALS, env=Envpar.WATER))

timesteps = 150
Time = range(timesteps)

md = gp.Model("gown_optimization")

def make_cost_vars(Options):
    total_impacts = {}
    partial_impacts = {}
    
    for x in Options:
        total_impacts[x] = md.addVars(Envpar, vtype=GRB.CONTINUOUS, name=f"TOTAL_IMPACTS_{x.Name}")
        partial_impacts[x] = md.addVars(Stages, Envpar, Time, vtype=GRB.CONTINUOUS, name=f"PARTIAL_IMPACTS_{x.Name}")

    return {"TOTAL": total_impacts, "PARTIAL": partial_impacts}

def make_decision_vars(options):
    dct_var = {}
    dct_var[Stages.ARRIVALMOM] = md.addVars(options, Time, vtype=GRB.BINARY, name="ARRIVALMOM")
    dct_var[Stages.NEWARRIVALS] = md.addVars(options, Time, vtype=GRB.INTEGER, name="NEWARRIVALS")
    dct_var[Stages.HOSPITAL] = md.addVars(options, Time, vtype=GRB.INTEGER, name="HOSPITAL")
    dct_var[Stages.LAUNDRY] = md.addVars(options, Time, vtype=GRB.INTEGER, name="LAUNDRY")
    dct_var[Stages.EOL] = md.addVars(options, Time, vtype=GRB.INTEGER, name="EOL")
    dct_var[Stages.LOST] = md.addVars(options, Time, vtype=GRB.INTEGER, name="LOST")
    dct_var[Stages.USAGE] = md.addVars(options, Time, vtype=GRB.INTEGER, name="USAGE")
    md.printStats()
    return dct_var

def initial_settings(Options, dv, initial_gowns=50):
    for x in Options:
        md.addConstr(dv[Stages.HOSPITAL][x, 0] == initial_gowns, name=f"initial_gowns_{x.Name}")
    return md

def gown_flow(dv):
    for t in Time[:-1]:
        for x in Options:
            md.addConstr(dv[Stages.HOSPITAL][x, t + 1] == dv[Stages.HOSPITAL][x, t] - dv[Stages.USAGE][x, t] + dv[Stages.LAUNDRY][x, t] + dv[Stages.NEWARRIVALS][x, t], name=f"HOSPITAL_balance_{x.Name}_{t}")
            md.addConstr(dv[Stages.USAGE][x, t] == dv[Stages.LOST][x, t + 1] + dv[Stages.LAUNDRY][x, t + 1] + dv[Stages.EOL][x, t + 1], name=f"USAGE_balance_{x.Name}_{t}")
            md.addConstr(dv[Stages.USAGE][x, t] <= dv[Stages.HOSPITAL][x, t], name=f"USAGE_limit_{x.Name}_{t}")
            md.addConstr(dv[Stages.LAUNDRY][x, t + 1] <= dv[Stages.USAGE][x, t] * x.Reusable, name=f"LAUNDRY_limit_{x.Name}_{t}")
    for t in Time:
        md.addConstr(gp.quicksum(dv[Stages.USAGE][x, t] for x in Options) == Specifications.usage_between_pickup, name=f"USAGE_total_{t}")
    return md

def calculate_costs(dv, cv):
    total_impacts = cv["TOTAL"]
    partial_impacts = cv["PARTIAL"]
    print(partial_impacts)
    md.addConstrs(partial_impacts[x][st, cs, t] == dv[st][x, t] * get_impact(x, st, cs) for cs in Envpar for st in Stages for x in Options for t in Time)
    for cs in Envpar:
        md.addConstrs(total_impacts[x][cs] == gp.quicksum(partial_impacts[x][st, cs, t] for st in Stages for t in Time) for x in Options)
    return md

def balance_reusable(dv, mn, mx):
    if mn > 1 or (mx < mn):
        mn, mx = 0.1, 0.9

    for t in Time:
        md.addConstr(gp.quicksum(dv[Stages.USAGE][x, t] for x in Options if x.Reusable) >= mn * Specifications.usage_between_pickup, name=f"BALANCE_reusable_{t}")
        md.addConstr(gp.quicksum(dv[Stages.USAGE][x, t] for x in Options if x.Reusable) <= mx * Specifications.usage_between_pickup, name=f"BALANCE_disposable_{t}")
    return md

dv = make_decision_vars(Options)
cv = make_cost_vars(Options)

md = initial_settings(Options, dv)
md = gown_flow(dv)
md = calculate_costs(dv, cv)
md = balance_reusable(dv, 0.1, 0.9)

md.setObjective(gp.quicksum(cv["TOTAL"][x][cs] for cs in Specifications.optimizer for x in Options), GRB.MINIMIZE)

md.printStats()
md.optimize()

if md.status == GRB.INFEASIBLE:
    print("Model is infeasible. Analyzing infeasibilities...")
    md.computeIIS()
    md.write("model.ilp")
    for c in md.getConstrs():
        if c.IISConstr:
            print(f"Infeasible constraint: {c.constrName}")
elif md.status == GRB.OPTIMAL:
    print("Results of gown usage for each variant:")
    for x in Options:
        usage_values = [dv[Stages.USAGE][x, t].X for t in Time]
        print(f"Gown '{x.Name}' with impacts {x.Impacts}:")
        print(f"Usage values: {usage_values}\n")
        print("Total impacts:")
        for cs in Envpar:
            print(f"{cs.name}: {cv['TOTAL'][x][cs].X}")
else:
    print("Optimization was not successful. Status code:", md.status)

best_option = min(Options, key=lambda x: sum(cv["TOTAL"][x][cs].X for cs in Envpar))
print(f"The best option is the gown '{best_option.Name}' with impacts {best_option.Impacts}.")
