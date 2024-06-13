import gurobipy as gp
from gurobipy import GRB
from enum import Enum

class Envpar(Enum):
    CO2EQ = 1
    WATER = 2
    ENERGY = 3
    MONEY = 4

class Flows(Enum):
    HOSPITAL = 1
    LAUNDRY = 2
    USAGE = 3
    LOST = 4
    EOL = 5
    ARRIVALMOM = 6
    NEWARRIVALS = 7

class Gown:
    def __init__(self, name, reusable, impacts):
        self.Name = name
        self.Reusable = reusable
        self.Impacts = impacts

class Specs:
    def __init__(self, usage_per_week, pickups_per_week):
        self.usage_per_week = usage_per_week
        self.pickups_per_week = pickups_per_week
        self.usage_between_pickup = self.usage_per_week / self.pickups_per_week

# Create set of specifications and optional gowns. This is the instance we model.
Options = [
    Gown(name="gown_1", reusable=0, impacts={Envpar.CO2EQ: 1, Envpar.WATER: 2, Envpar.ENERGY: 3, Envpar.MONEY: 2}),
    Gown(name="gown_2", reusable=1, impacts={Envpar.CO2EQ: 0.5, Envpar.WATER: 1, Envpar.ENERGY: 1.5, Envpar.MONEY: 5}),
    Gown(name="gown_3", reusable=1, impacts={Envpar.CO2EQ: 0.8, Envpar.WATER: 1.5, Envpar.ENERGY: 2, Envpar.MONEY: 7})
]
Specifications = Specs(usage_per_week=100, pickups_per_week=2)

# Create Decision Model
md = gp.Model("gown_optimization")

# Create Decision Variables
timesteps = 150
Time = range(timesteps)

def make_decision_vars(options):
    dct_var = {}
    dct_var[Flows.ARRIVALMOM] = md.addVars(options, Time, vtype=GRB.BINARY, name="ARRIVALMOM")
    dct_var[Flows.NEWARRIVALS] = md.addVars(options, Time, vtype=GRB.INTEGER, name="NEWARRIVALS")
    dct_var[Flows.HOSPITAL] = md.addVars(options, Time, vtype=GRB.INTEGER, name="HOSPITAL")
    dct_var[Flows.LAUNDRY] = md.addVars(options, Time, vtype=GRB.INTEGER, name="LAUNDRY")
    dct_var[Flows.EOL] = md.addVars(options, Time, vtype=GRB.INTEGER, name="EOL")
    dct_var[Flows.LOST] = md.addVars(options, Time, vtype=GRB.INTEGER, name="LOST")
    dct_var[Flows.USAGE] = md.addVars(options, Time, vtype=GRB.INTEGER, name="USAGE")
    return dct_var

def make_cost_vars():
    cst_var = md.addVars(Envpar, vtype=GRB.CONTINUOUS, name="COSTS")
    return cst_var

# Create Decision Variables
dv = make_decision_vars(Options)
cv = make_cost_vars()

# Initialize the hospital gowns at time 0
initial_gowns = 50
for x in Options:
    md.addConstr(dv[Flows.HOSPITAL][x, 0] == initial_gowns, name=f"initial_gowns_{x.Name}")

# Constraints to manage the flow of gowns
def gown_flow(dv):
    for t in Time[:-1]:
        for x in Options:
            md.addConstr(dv[Flows.HOSPITAL][x, t + 1] == dv[Flows.HOSPITAL][x, t] - dv[Flows.USAGE][x, t] + dv[Flows.LAUNDRY][x, t] + dv[Flows.NEWARRIVALS][x, t], name=f"HOSPITAL_balance_{x.Name}_{t}")
            md.addConstr(dv[Flows.USAGE][x, t] == dv[Flows.LOST][x, t + 1] + dv[Flows.LAUNDRY][x, t + 1] + dv[Flows.EOL][x, t + 1], name=f"USAGE_balance_{x.Name}_{t}")
            md.addConstr(dv[Flows.USAGE][x, t] <= dv[Flows.HOSPITAL][x, t], name=f"USAGE_limit_{x.Name}_{t}")
            md.addConstr(dv[Flows.LAUNDRY][x, t + 1] <= dv[Flows.USAGE][x, t] * x.Reusable, name=f"LAUNDRY_limit_{x.Name}_{t}")
    for t in Time:
        md.addConstr(gp.quicksum(dv[Flows.USAGE][x, t] for x in Options) == Specifications.usage_between_pickup, name=f"USAGE_total_{t}")

gown_flow(dv)

# Calculate costs
def calculate_costs(dv, cv):
    for cs in Envpar:
        md.addConstr(cv[cs] == gp.quicksum(dv[flow][x, t] * x.Impacts[cs] for x in Options for flow in Flows for t in Time), name=f"COST_{cs}")

calculate_costs(dv, cv)

# Calculate total impacts for each gown
total_impacts = {}
for x in Options:
    total_impacts[x] = md.addVars(Envpar, vtype=GRB.CONTINUOUS, name=f"TOTAL_IMPACTS_{x.Name}")
    for cs in Envpar:
        md.addConstr(total_impacts[x][cs] == gp.quicksum(dv[Flows.USAGE][x, t] * x.Impacts[cs] for t in Time), name=f"TOTAL_IMPACT_{cs.name}_{x.Name}")

# Add balance constraint to ensure all gown types are used if possible
for t in Time:
    md.addConstr(gp.quicksum(dv[Flows.USAGE][x, t] for x in Options if x.Reusable) >= 0.5 * Specifications.usage_between_pickup, name=f"BALANCE_reusable_{t}")
    md.addConstr(gp.quicksum(dv[Flows.USAGE][x, t] for x in Options if not x.Reusable) >= 0.5 * Specifications.usage_between_pickup, name=f"BALANCE_disposable_{t}")

# Set objective to minimize all environmental impacts and costs
md.setObjective(gp.quicksum(cv[cs] for cs in Envpar), GRB.MINIMIZE)

# Optimize the model
md.optimize()

# Check if the model is optimized successfully
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
        usage_values = [dv[Flows.USAGE][x, t].X for t in Time]
        print(f"Gown '{x.Name}' with impacts {x.Impacts}:")
        print(f"Usage values: {usage_values}\n")
        print("Total impacts:")
        for cs in Envpar:
            print(f"{cs.name}: {total_impacts[x][cs].X}")
else:
    print("Optimization was not successful. Status code:", md.status)

# Identify the best option based on the total costs and impacts
best_option = min(Options, key=lambda x: sum(total_impacts[x][cs].X for cs in Envpar))
print(f"The best option is the gown '{best_option.Name}' with impacts {best_option.Impacts}.")
