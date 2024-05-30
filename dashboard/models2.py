import gurobipy as gp
from gurobipy import GRB
import numpy as np
from enum import Enum

from models import Material
from models import Gown

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


class Specs(models.Model):
    usage_per_week = models.IntegerField()
    usage_per_weekday = models.IntegerField()
    pickups_per_week = models.IntegerField()
    usage_between_pickup = int(self.usage_per_week/self.pickups_per_week)

#Create set of specifications and optional gowns. This is the instance we model.

Options = [Gown(),Gown(),Gown()]
Specifications = Specs()

#Create Decision Model
md = gp.Model("ip")

#Create Decision variables
#We model everything between pickups to the laundry. We refer to this as one time frame
#A gown can only be used once during a time frame, and if used, cannot be used in the next time frame (due to laundry or not being reusable)
#Lets go for 150 pickups
timesteps = 150
Time = range(-1,timesteps)

def time_wo(excl):
    return [t for t in Time if t not in excl]

def create_env_db(gownOptions):
    envDict = {}
    for o in gownOptions:
        envDict[o]={}
        for s in Flows:
            envDict[o][s] = {}
            for e in Envirpar:
                envDict[o][s][e] = 0
    return envDict

def get_parameter(gown,phase,unit):
    return envDict[gown][phase][unit]

def make_decision_vars(Options):
    dct_var = {}
    
    dct_var[Flows.ARRIVALMOM] =  md.Vars(Options,time,GRB.BINARY) #Indicator if gowns arrive on time
    dct_var[Flows.NEWARRIVALS] = md.Vars(Options,Time,GRB.INTEGER) #Newly arrived gowns, usable in the next time-frame.
    dct_var[Flows.HOSPITAL]= md.Vars(Options,Time,GRB.INTEGER) #Gowns that are present for use within the hospital logistics.
    dct_var[Flows.LAUNDRY] = md.Vars(Options,Time,GRB.INTEGER) #Gowns that are at the laundry; we assume they get back to the hospital at the next time-step.
    dct_var[Flows.EOL] = md.Vars(Options,Time,GRB.INTEGER) #Gowns that are thrown away in a ordered fashion (not lost).
    dct_var[Flows.LOST] = md.Vars(options,Time,GRB.INTEGER) #Gowns that are lost somewhere in the process after being used.
    dct_var[Flows.USAGE] = md.Vars(options, Time,GRB.INTEGER) #Gowns that are used at each timeframe
    return dct_var


def make_costs_vars():
    #Make the variables that collect all costs. 
    cst_var = {}
    for cs in Envirpar:
        cst_var[cs] = md.Var(GRB.INTEGER)

    return cst_var

def gown_flow(dv):
    ##Constraints that manage the flow and ensure that there are enough gowns at all time
    #New gowns arrive in the system, gowns are moved from laundry to the hospital, and used gowns move somewhere else for the next time frame
    md.Constrs(dv[Flows.HOSPITAL][x,t+1] == dv[Flows.HOSPITAL][x,t] - dv[Flows.USAGE][x,t] + dv[Flows.LAUNDRY][x,t] + dv[Flows.NEWARRIVAL][x,t] 
               for x in Options for t in time_wo([-1,timesteps-1]))

    #All used  gowns either get washed, get thrown away or we lost them somewhere in the next phase
    md.Constrs(dv[Flows.USAGE][x,t] == dv[Flows.LOST][x,t+1] + dv[Flows.LAUNDRY][x,t+1] + dv[Flows.EOL][x,t+1] for x in Options for t in time_wo([-1,timesteps-1]))

    #There must be enough gowns to use, and they are used every timestep
    md.Constrs(dv[Flows.USAGE][x,t] <= dv[Flows.HOSPITAL][x,t] for x in Options for t in time_wo([1]))
    md.Constrs(sum([dv[Flows.USAGE][x,t] for x in Options]) == Specifications.usage_between_pickup for t in time_wo([]))
    
    #When a gown is single use, no gowns should go to the laundry.
    md.Constrs(dv[Flows.LAUNDRY][x,t+1] <= dv[Flows.USAGE][x,t]*x.Reusable for x in Options for t in time_wo([-1,timesteps-1]))

def all_costs(dv,ev,cv):
    #dv = all flowvariables. #ev = all environmental parameters, cv = all cost variables
    #Everything that is relevant per gown; 
    md.Constrs(cv[cs] == sum([dv[stage][x,t]*ev[x][stage][cs] for x in Options for stage in Flows for t in Time]) for cs in Envpar)

    #All costs of all sorts associated to all actions must be collected here
    pass

def objectives(obj_list):
    #Make all objectives
    #obj_list should be a list of preferences. Or maybe even more complicated.
    pass
