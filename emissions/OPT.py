import pyscipopt as ps
from pyscipopt import quicksum
from enum import Enum
import itertools


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

Accountables = [Stages.NEWARRIVALS, Stages.LAUNDRY, Stages.LOST, Stages.EOL, Stages.ARRIVALMOM]

LARGEVALUE = 10000

class Gown:
    def __init__(self, name, reusable, impacts):
        self.Name = name
        self.Reusable = reusable
        self.Impacts = impacts

class Specs:
    def __init__(self, usage_per_week, pickups_per_week, optimizer=[Envpar.MONEY], loss_percentage=0.001):
        self.usage_per_week = usage_per_week
        self.pickups_per_week = pickups_per_week
        self.usage_between_pickup = self.usage_per_week / self.pickups_per_week
        self.loss_percentage = loss_percentage
        self.optimizer = optimizer

def varsList(*lsts):
    if len(lsts) > 1:
        retlist = list(itertools.product(*lsts))
    else:
        retlist = lsts[0]
    return retlist

def get_impact(gown, stage, env):
    if stage not in Accountables:
        return 0
    else:
        yvar = gown.Impacts["envpars"].index(env.name)
        xvar = gown.Impacts["stages"].index(stage.name)
        return gown.Impacts["params"][xvar][yvar]

class GownOptimizer:
    def __init__(self, gown_data, specifications):
        self.Options = self.create_gowns(gown_data)
        self.Specifications = Specs(**specifications)
        self.timesteps = 150
        self.Time = range(self.timesteps)
        self.md = ps.Model("gown_optimization")
        self.md.hideOutput(True)
        self.dv = self.make_decision_vars()
        self.cv = self.make_cost_vars()

    def create_gowns(self, gown_data):
        return [Gown(name=gw["name"], reusable=gw["reusable"], impacts=gw["impacts"]) for gw in gown_data]

    def make_decision_vars(self):
        options_time = varsList(self.Options, self.Time)
        dct_var = {}
        for stage in Stages:
            dct_var[stage] = {}
            for x, t in options_time:
                dct_var[stage][x, t] = self.md.addVar(vtype="I" if stage != Stages.ARRIVALMOM else "B", name=f"{stage.name}_{x.Name}_{t}")
        return dct_var

    def make_cost_vars(self):
        total_impacts = {}
        partial_impacts = {}
        var_list = varsList([s.name for s in Stages], [e.name for e in Envpar], self.Time)
        
        for x in self.Options:
            total_impacts[x] = self.addVars([e.name for e in Envpar], "C")
            partial_impacts[x] = self.addVars(var_list, "C")

        return {"TOTAL": total_impacts, "PARTIAL": partial_impacts}

    def addVars(self, varlist, vtype):
        return {x: self.md.addVar(vtype=vtype, name=str(x)) for x in varlist}

    def initial_settings(self, initial_gowns=None):
        if initial_gowns is None:
            initial_gowns = [2000] + [0] * (len(self.Options) - 1)
        elif isinstance(initial_gowns, int):
            initial_gowns = [initial_gowns] * len(self.Options)
        elif isinstance(initial_gowns, list):
            if len(initial_gowns) != len(self.Options):
                raise ValueError(f"initial_gowns list length ({len(initial_gowns)}) must match number of gown options ({len(self.Options)})")
        else:
            raise ValueError("Invalid initial_gowns parameter")

        for ix, x in enumerate(self.Options):
            self.md.addCons(self.dv[Stages.HOSPITAL][x, 0] == initial_gowns[ix], name=f"initial_gowns_{x.Name}")
            self.md.addCons(self.dv[Stages.LAUNDRY][x, 0] == 0)
            self.md.addCons(self.dv[Stages.EOL][x, 0] == 0)
            self.md.addCons(self.dv[Stages.LOST][x, 0] == 0)

    def gown_flow(self):
        for t in self.Time[:-1]:
            for x in self.Options:
                self.md.addCons(self.dv[Stages.HOSPITAL][x, t + 1] == 
                                self.dv[Stages.HOSPITAL][x, t] - 
                                self.dv[Stages.USAGE][x, t] + 
                                self.dv[Stages.LAUNDRY][x, t] + 
                                self.dv[Stages.NEWARRIVALS][x, t],
                                name=f"HOSPITAL_balance_{x.Name}_{t}")
                self.md.addCons(self.dv[Stages.USAGE][x, t] == 
                                self.dv[Stages.LOST][x, t + 1] + 
                                self.dv[Stages.LAUNDRY][x, t + 1] + 
                                self.dv[Stages.EOL][x, t + 1],
                                name=f"USAGE_balance_{x.Name}_{t}")
                self.md.addCons(self.dv[Stages.USAGE][x, t] <= self.dv[Stages.HOSPITAL][x, t],
                                name=f"USAGE_limit_{x.Name}_{t}")
                self.md.addCons(self.dv[Stages.LAUNDRY][x, t + 1] <= self.dv[Stages.USAGE][x, t] * x.Reusable,
                                name=f"LAUNDRY_limit_{x.Name}_{t}")
                self.md.addCons(self.dv[Stages.NEWARRIVALS][x, t] <= self.dv[Stages.ARRIVALMOM][x, t] * LARGEVALUE,
                                name=f"NEWARRIVALS_limit_{x.Name}_{t}")

        for t in self.Time:
            self.md.addCons(quicksum(self.dv[Stages.USAGE][x, t] for x in self.Options) == self.Specifications.usage_between_pickup,
                            name=f"USAGE_total_{t}")

    def calculate_costs(self):
        total_impacts = self.cv["TOTAL"]
        partial_impacts = self.cv["PARTIAL"]
        for cs in Envpar:
            cs_name = cs.name
            for st in Stages:
                st_name = st.name
                for x in self.Options:
                    for t in self.Time:
                        self.md.addCons(
                            partial_impacts[x][st_name, cs_name, t] == 
                            self.dv[st][x, t] * get_impact(x, st, cs)
                        )
        
        for cs in Envpar:
            cs_name = cs.name
            for x in self.Options:
                self.md.addCons(
                    total_impacts[x][cs_name] == 
                    quicksum(partial_impacts[x][st.name, cs_name, t] 
                             for st in Stages for t in self.Time)
                )

    def balance_reusable(self, mn, mx):
        if mn > 1 or (mx < mn):
            mn, mx = 0.1, 0.9

        self.md.addCons(quicksum(self.dv[Stages.USAGE][x, t] for t in self.Time for x in self.Options if x.Reusable) >= 
                        mn * quicksum(self.dv[Stages.USAGE][x, t] for t in self.Time for x in self.Options),
                        name="BALANCE_reusable")
        self.md.addCons(quicksum(self.dv[Stages.USAGE][x, t] for t in self.Time for x in self.Options if x.Reusable) <= 
                        mx * quicksum(self.dv[Stages.USAGE][x, t] for t in self.Time for x in self.Options),
                        name="BALANCE_disposable")

    def build_buffer(self, factor=10):
        for t in self.Time:
            if t > 1:
                self.md.addCons(quicksum(self.dv[Stages.HOSPITAL][x, t] for x in self.Options) >= 
                                factor * self.Specifications.usage_between_pickup,
                                name=f"BUFFER_{t}")

    def estimate_gown_loss(self):
        for x in self.Options:
            for t in self.Time:
                if t % 10 == 9:
                    self.md.addCons(quicksum(self.dv[Stages.LOST][x, t - tx] - 
                                             self.Specifications.loss_percentage * self.dv[Stages.USAGE][x, t - tx - 1] 
                                             for tx in range(0, 9)) >= 0,
                                    name=f"GOWN_LOSS_{x.Name}_{t}")

    def optimize(self):
        self.initial_settings()
        self.gown_flow()
        self.calculate_costs()
        self.balance_reusable(0.6, 1)
        self.build_buffer()
        self.estimate_gown_loss()

        self.md.setObjective(quicksum(self.cv["TOTAL"][x][cs] for cs in self.Specifications.optimizer for x in self.Options), 'minimize')
        self.md.setParam('limits/time', 20)

        self.md.optimize()

        if self.md.getStatus() == "infeasible":
            return self.handle_infeasible_model()
        else:
            return self.get_optimization_results()

    def handle_infeasible_model(self):
        self.md.computeIIS()
        self.md.write("model.ilp")
        infeasible_constraints = [c.constrName for c in self.md.getConstrs() if c.IISConstr]
        return {"status": "infeasible", "infeasible_constraints": infeasible_constraints}

    # def get_optimization_results(self):
    #     results = {}
    #     for x in self.Options:
    #         usage_values = [int(self.md.getVal(self.dv[Stages.USAGE][x, t])) for t in self.Time]
    #         new_arrivals = [(t, int(self.md.getVal(self.dv[Stages.NEWARRIVALS][x,t]))) for t in self.Time if self.md.getVal(self.dv[Stages.NEWARRIVALS][x,t]) > 0]
    #         total_impact = {cs.name: self.md.getVal(self.cv["TOTAL"][x][cs.name]) for cs in Envpar}
            
    #         results[x.Name] = {
    #             "usage_values": usage_values,
    #             "new_arrivals": new_arrivals,
    #             "total_impact": total_impact
    #         }
    #     return {"status": "optimal", "results": results}
    

    def get_optimization_results(self):
        results = {}
        for x in self.Options:
            usage_values = [int(self.md.getVal(self.dv[Stages.USAGE][x, t])) for t in self.Time]
            new_arrivals = [(t, int(self.md.getVal(self.dv[Stages.NEWARRIVALS][x,t]))) for t in self.Time if self.md.getVal(self.dv[Stages.NEWARRIVALS][x,t]) > 0]
            total_impact = {cs.name: self.md.getVal(self.cv["TOTAL"][x][cs.name]) for cs in Envpar}
                
                # New code to calculate impacts per stage
            stage_impacts = {}
            for st in Stages:
                stage_impacts[st.name] = {}
                for cs in Envpar:
                        # Evaluate the quicksum expression to get a numerical value
                    stage_impacts[st.name][cs.name] = self.md.getVal(quicksum(self.dv[st][x, t] * get_impact(x, st, cs) for t in self.Time))

            results[x.Name] = {
                "usage_values": usage_values,
                "new_arrivals": new_arrivals,
                "Impacts": {
                    "stages": stage_impacts,  # Include impacts per stage
                    "total_impact": total_impact
                }
            }
        return {"status": "optimal", "results": results}
