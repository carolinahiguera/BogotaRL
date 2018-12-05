'''
Created on Nov 27, 2017

@author: carolina
'''

import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
import numpy as np
import pandas as pd

import TLS
import junction
import var


def getObservation():
    for tls in var.agent_TLS.keys():
        for j in range(0,len(var.agent_TLS[tls].listJunctions)):
            junction = var.agent_TLS[tls].listJunctions[j]
            for edge in range(0,len(var.junctions[junction].edges)):
                for lane in range(0,len(var.junctions[junction].lanes[edge])):
                    lane_name = var.junctions[junction].lanes[edge][lane]
                    var.agent_TLS[tls].queueLaneTracker[j][edge][lane] = traci.lane.getLastStepHaltingNumber(lane_name)
                    var.agent_TLS[tls].waitingLaneTracker[j][edge][lane] = traci.lane.getWaitingTime(lane_name)/60.0 #EN MINUTOS
                    var.agent_TLS[tls].speedLaneTracker[j][edge][lane] = traci.lane.getLastStepMeanSpeed(lane_name) #EN M/S
                var.agent_TLS[tls].queueEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].queueLaneTracker[j][edge])
                var.agent_TLS[tls].waitingEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].waitingLaneTracker[j][edge])
                var.agent_TLS[tls].speedEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].speedLaneTracker[j][edge])

def getObservation2(currSod):
    for tls in var.agent_TLS.keys():
        if (var.agent_TLS[tls].finishPhase[1]) or (currSod%var.sampleTime == 0):
            for j in range(0,len(var.agent_TLS[tls].listJunctions)):
                junction = var.agent_TLS[tls].listJunctions[j]
                for edge in range(0,len(var.junctions[junction].edges)):
                    for lane in range(0,len(var.junctions[junction].lanes[edge])):
                        lane_name = var.junctions[junction].lanes[edge][lane]
                        var.agent_TLS[tls].queueLaneTracker[j][edge][lane] = traci.lane.getLastStepHaltingNumber(lane_name)
                        var.agent_TLS[tls].waitingLaneTracker[j][edge][lane] = traci.lane.getWaitingTime(lane_name)/60.0 #EN MINUTOS
                        var.agent_TLS[tls].speedLaneTracker[j][edge][lane] = traci.lane.getLastStepMeanSpeed(lane_name) #EN M/S
                    var.agent_TLS[tls].queueEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].queueLaneTracker[j][edge])
                    var.agent_TLS[tls].waitingEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].waitingLaneTracker[j][edge])
                    var.agent_TLS[tls].speedEdgeTracker[j][edge] = np.sum(var.agent_TLS[tls].speedLaneTracker[j][edge])
  

def getObservation_NB(tls, nb, currSod):
    #estado del agente tls
    stateDataEntry = [int(currSod/3600)+6]
    for j in range(0,len(var.agent_TLS[tls].listJunctions)):
        jID = var.agent_TLS[tls].listJunctions[j]
        for e in range(0,len(var.junctions[jID].edges)):
            stateDataEntry.append(var.agent_TLS[tls].queueEdgeTracker[j][e])
    for j in range(0,len(var.agent_TLS[tls].listJunctions)):
        jID = var.agent_TLS[tls].listJunctions[j]
        for e in range(0,len(var.junctions[jID].edges)):
            stateDataEntry.append(var.agent_TLS[tls].waitingEdgeTracker[j][e])
   #estado de su vecino
    if(nb != -1):
        for j in range(0,len(var.agent_TLS[nb].listJunctions)):
            jID = var.agent_TLS[nb].listJunctions[j]
            for e in range(0,len(var.junctions[jID].edges)):
                stateDataEntry.append(var.agent_TLS[nb].queueEdgeTracker[j][e])
        for j in range(0,len(var.agent_TLS[nb].listJunctions)):
            jID = var.agent_TLS[nb].listJunctions[j]
            for e in range(0,len(var.junctions[jID].edges)):
                stateDataEntry.append(var.agent_TLS[nb].waitingEdgeTracker[j][e])
    return stateDataEntry
       
  
        
    
    