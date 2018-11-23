'''
Created on Nov 27, 2017

@author: carolina
'''

import os, sys
import subprocess
#sys.path.append("/home/carolina/Instaladores/sumo-0.31.0")
sys.path.append("/Users/CarolinaHiguera/Programas/sumo-0.27.1/tools")
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
  
    
  
        
    
    