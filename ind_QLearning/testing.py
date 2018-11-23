'''
Created on Nov 2018

@author: carolina

independent learning
'''

import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo" #sumo-gui
import random
import pandas as pd
import numpy as np
import math
import var
import gets

dfSpeedTracker = {}
dfQueueTracker = {}
dfWaitingTracker = {} 
dfActions = {}
dfEpsilon = {}

def saveData(currSod):
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dfActions
    #Queues and waiting times
    for j in var.junctions.keys():
        auxQ = [currSod]
        auxW = [currSod]
        auxS = [currSod]
        for edge in range(0,len(var.junctions[j].edges)):
            junction = var.agent_TLS[var.junctions[j].tls].listJunctions.index(j)
            queue = var.agent_TLS[var.junctions[j].tls].queueEdgeTracker[junction][edge]
            waitTime = var.agent_TLS[var.junctions[j].tls].waitingEdgeTracker[junction][edge]
            speed = var.agent_TLS[var.junctions[j].tls].speedEdgeTracker[junction][edge]
            auxQ.append(queue)
            auxW.append(waitTime)
            auxS.append(speed)
        df = pd.DataFrame([auxQ])
        dfQueueTracker[j] = dfQueueTracker[j].append(df, ignore_index=True) 
        df = pd.DataFrame([auxW])
        dfWaitingTracker[j] = dfWaitingTracker[j].append(df, ignore_index=True)
        df = pd.DataFrame([auxS])
        dfSpeedTracker[j] = dfSpeedTracker[j].append(df, ignore_index=True)
    #Actions
    auxA = [currSod]
    for tls in var.agent_TLS.keys():
        auxA.append(var.agent_TLS[tls].currAction)
    df = pd.DataFrame([auxA])
    dfActions = dfActions.append(df, ignore_index=True)


def data2files(day):
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dfActions
    #Save actions and epsilons in file
    aux = ['sec']
    for tls in var.agent_TLS.keys():
        aux.append('tls_' + str(tls))
    dfActions.columns = aux
    dfActions.to_csv('./csv_files_test/indQ_actions_day' + str(day) + '.csv')
    
    #Save queues and times for each junction
    for j in var.junctions.keys():
        aux = ['currSod']        
        for edge in var.junctions[j].edges:
            aux.append(edge)
        dfQueueTracker[j].columns = aux
        dfWaitingTracker[j].columns = aux
        dfSpeedTracker[j].columns = aux
        dfQueueTracker[j].to_csv('./csv_files_test/indQ_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv')
        dfWaitingTracker[j].to_csv('./csv_files_test/indQ_times_' + var.junctions[j].name + '_day' + str(day) + '.csv')
        dfSpeedTracker[j].to_csv('./csv_files_test/indQ_speed_' + var.junctions[j].name + '_day' + str(day) + '.csv')

def ind_QLearning():  
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dfActions  
        
    for day in range(0,var.episodesTest):
        fileOut = open("days.csv","w")
        fileOut.write("Testing day: "+str(day)+"\n")
        fileOut.close()
        
        sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
        traci.start(sumoCmd)    
        
        dfSpeedTracker = {}
        dfQueueTracker = {}
        dfWaitingTracker = {} 
        dfActions = pd.DataFrame()
        
        for j in var.junctions.keys():  
            dfQueueTracker[j] = pd.DataFrame()
            dfWaitingTracker[j] = pd.DataFrame()  
            dfSpeedTracker[j] = pd.DataFrame()  
        
        #Begins simulation of 1 day           
        for currSod in range(0,var.secondsInDay):
            if(currSod%var.sampleTime == 0):
                #Get new state    
                gets.getObservation()
                for tls in var.agent_TLS.keys():
                    if var.agent_TLS[tls].finishAuxPhase:
                        var.agent_TLS[tls].applyPolicy(currSod)
                saveData(currSod)

                #Apply phases
                for tls in var.agent_TLS:
                    var.agent_TLS[tls].setPhase(currSod)
                    traci.trafficlights.setRedYellowGreenState(str(tls), 
                        var.agent_TLS[tls].RedYellowGreenState)
            traci.simulationStep()
        traci.close()
        #End simulation of 1 day
        data2files(day)
    #-----------------------------------------------------
    fileOut = open("days.csv","w")
    fileOut.write("End testing \n")
    fileOut.close()
