import gurobipy as gp
from gurobipy import GRB
import numpy as np
from enum import Enum

from models import Material
from models import Gown

class Stages(Enum):
    PRODUCTION = 1
    LAUNDRY = 2
    SPEC_EOL = 3
    INCAR = 4
    TRANSPORT = 5

class Envirpar(Enum):
    COEQ = 1
    WATER = 2
    ENERGY = 3
    MONEY = 4
    
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
        for s in Stages:
            envDict[o][s] = {}
            for e in Envirpar:
                envDict[o][s][e] = 0

    return envDict

def get_parameter(gown,phase,unit):
    return envDict[gown][phase][unit]

def make_decision_vars(Options):
    arrivalMoments = md.Vars(Options,time,GRB.BINARY) #Indicator if gowns arrive on time
    newArrival = md.Vars(Options,Time,GRB.INTEGER) #Newly arrived gowns, usable in the next time-frame.
    atHospital = md.Vars(Options,Time,GRB.INTEGER) #Gowns that are present for use within the hospital logistics.
    atLaundry = md.Vars(Options,Time,GRB.INTEGER) #Gowns that are at the laundry; we assume they get back to the hospital at the next time-step.
    toDisposal = md.Vars(Options,Time,GRB.INTEGER) #Gowns that are thrown away in a ordered fashion (not lost).
    lostInSystem = md.Vars(options,Time,GRB.INTEGER) #Gowns that are lost somewhere in the process after being used.
    usedPhase = md.Vars(options, Time,GRB.INTEGER) #Gowns that are used at each timeframe

def gown_flow():
    ##Constraints that manage the flow and ensure that there are enough gowns at all time
    #New gowns arrive in the system, gowns are moved from laundry to the hospital, and used gowns move somewhere else for the next time frame
    md.Constrs(atHospital[x,t+1] == atHospital[x,t] - usedPhase[x,t] + atLaundry[x,t] + newArrival[x,t] for x in Options for t in time_wo([-1,timesteps-1]))

    #All used  gowns either get washed, get thrown away or we lost them somewhere in the next phase
    md.Constrs(usedPhase[x,t] == lostInSystem[x,t+1] + atLaundry[x,t+1] + toDisposal[x,t+1] for x in Options for t in time_wo([-1,timesteps-1]))

    #There must be enough gowns to use, and they are used every timestep
    md.Constrs(usedPhase[x,t] <= atHospital[x,t] for x in Options for t in time_wo([1]))
    md.Constrs(sum([usedPhase[x,t] for x in Options]) == Specifications.usage_between_pickup for t in time_wo([]))

def all_costs_vars():
    #All cost variables 
    #We should call on a database/json/csv where all the sorts of relevant pollutions and costs per gown type are stored
    pass

def all_costs():
    #All costs of all sorts associated to all actions must be collected here
    pass

def objectives():
    #Make all objectives
    pass
