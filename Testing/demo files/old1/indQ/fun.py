'''
Created on 22/09/2016

@author: carolina
'''
import os, sys
import subprocess

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(tools)
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
sumoBinary = "sumo" #sumo-gui
sumoCmd = [sumoBinary, "-c", "../miniCity/miniCity-tf.sumo.cfg", "--no-step-log", "true"]

import random
import pandas as pd
import numpy as np
import sklearn
from sklearn.cluster import KMeans
import pickle
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import var


listMeanReward = []
listMedianReward = []
listMinReward = []

def computeReward(agtID, queueTracker, waitingTracker):
    reward = 0
    for key in var.agentsQ[agtID].listEdges:
        reward -= ((var.agentsQ[agtID].beta[0]*queueTracker[key])**var.agentsQ[agtID].theta[0] + (var.agentsQ[agtID].beta[1]*waitingTracker[key])**var.agentsQ[agtID].theta[1]) 
    return reward

def learnDiscretization(daysToObserve):
    global listMeanReward, listMedianReward, listMinReward
    
    for sl in var.SLs:
        var.agentsQ[sl].initAgent()
    
    stateData = {}
    for agt in range(0,var.numAgents):
        stateData[agt]={}
        for h in range(0,var.hoursInDay):
            stateData[agt][h]={}
            for act in var.agentsQ[agt].actionPhases:
                stateData[agt][h][act]=np.array([])    
    
    
    for day in range(daysToObserve):

        fileOut = open("days.csv","w")
        fileOut.write("Observation day: "+str(day)+"\n")
        fileOut.close()

        traci.start(sumoCmd)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        
        for sl in var.SLs:        
            dfRewVals[sl] = pd.DataFrame()
            dfQueueTracker[sl] = pd.DataFrame()
            dfWaitingTracker[sl] = pd.DataFrame()        
        
        hod = 0
        currSod = 0
                
        while currSod < var.secondsInDay:
            for sl in var.SLs:
                planName = traci.trafficlights.getProgram(str(sl))
                idPhase = int(traci.trafficlights.getPhase(str(sl)))
                phase = var.agentsQ[sl].planProgram[planName][idPhase]
                if(var.agentsQ[sl].currPhaseID == phase and currSod != 0): # if phase HAS NOT changed
                    var.agentsQ[sl].secsThisPhase += 1 # increase the seconds in the currentPhase 
                else: # IF THE PHASE HAS CHANGED
                    var.agentsQ[sl].secsThisPhase = 0
                    var.agentsQ[sl].currPhaseID = phase
            
            #end of yellow phase for some intersection?
            changePhase = [0 == (var.agentsQ[sl].currPhaseID)%2 for sl in var.SLs]
            changeSec = [0 == var.agentsQ[sl].secsThisPhase for sl in var.SLs]
            change = [1==changePhase[i]*changeSec[i] for i in var.SLs]
            
#             if(var.agentsQ[0].currPhaseID==0 and var.agentsQ[1].currPhaseID==0):
#                 print('si esta')
            
            if (True in change):
                agentChanged = [sl for sl in range(var.numAgents) if((changePhase[sl]*changeSec[sl])==1)] #Agents ID who changed phase
                
                #============  HOD
                if hod != currSod/var.secondsInHour:
                    hod = int(currSod/var.secondsInHour)
                    print('observation day = ', day)
                    print('hour = ', hod)
                    
                                   
                
                #=========== UPDATE INFORMATION OF ALL AGENTS WHO CHANGED THEIR PHASE
                for agt in agentChanged:
                    #================= count halted vehicles (4 elements)
                    for lane in var.agentsQ[agt].listLanes:
                        var.agentsQ[agt].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.agentsQ[agt].listEdges:
                        var.agentsQ[agt].queueTracker[edge] = 0
                        for lane in range(var.agentsQ[agt].numberLanes[idx]):
                            var.agentsQ[agt].queueTracker[edge] += var.agentsQ[agt].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    
                    # ================ cum waiting time in minutes
                    for lane in var.agentsQ[agt].listLanes:
                        var.agentsQ[agt].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.agentsQ[agt].listEdges:
                        var.agentsQ[agt].waitingTracker[edge] = 0
                        for lane in range(var.agentsQ[agt].numberLanes[idx]):
                            var.agentsQ[agt].waitingTracker[edge] += var.agentsQ[agt].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    
                #============= UPDATE STATES FOR EACH NEIGHBOUR PAIR
                for agt in agentChanged:
                    stateDataEntry = []
                    for edge in var.agentsQ[agt].listEdges:
                        stateDataEntry.append(var.agentsQ[agt].queueTracker[edge])
                    for edge in var.agentsQ[agt].listEdges:
                        stateDataEntry.append(var.agentsQ[agt].waitingTracker[edge])
                    currAction = var.agentsQ[agt].currPhaseID
                    if len(stateData[agt][hod][currAction]) == 0:
                        stateData[agt][hod][currAction] = np.array([stateDataEntry])
                    else:
                        stateData[agt][hod][currAction] = np.vstack([stateData[agt][hod][currAction], stateDataEntry])
                    
#                     nAgt = var.neighborsPerAgent[agt]
#                     for nb in nAgt:
#                         pair = var.neighborsList[nb]
#                         stateDataEntry = []
#                         for sl in pair:                        
#                             for edge in var.agentsQ[sl].listEdges:
#                                 stateDataEntry.append(var.agentsQ[sl].queueTracker[edge])
#                             for edge in var.agentsQ[sl].listEdges:
#                                 stateDataEntry.append(var.agentsQ[sl].waitingTracker[edge])
#                         currJointAction = var.agentsQ[pair[0]].getJointAction(pair[1])
#                         if len(stateData[nb][hod][currJointAction]) == 0:
#                             stateData[nb][hod][currJointAction] = np.array([stateDataEntry])
#                         else:
#                             stateData[nb][hod][currJointAction] = np.vstack([stateData[nb][hod][currJointAction], stateDataEntry])
                                             
                    # ================= track reward function
                    currRewValue = computeReward(agt, var.agentsQ[agt].queueTracker, var.agentsQ[agt].waitingTracker)
                    df = pd.DataFrame([[currSod, currRewValue]]) 
                    dfRewVals[agt] = dfRewVals[agt].append(df, ignore_index=True)
            currSod += 1           
            traci.simulationStep() 
        traci.close() #End one day of observation    
        
        aux = {}
        for i in range(0,3):
            aux[i] = []
        for sl in var.SLs:
            aux[0].append(dfRewVals[sl].mean(axis = 0)[1])
            aux[1].append(dfRewVals[sl].median(axis = 0)[1])
            aux[2].append(dfRewVals[sl].min(axis = 0)[1])
        listMeanReward.append(aux[0])
        listMedianReward.append(aux[1])
        listMinReward.append(aux[2]) 
                  
    #End of observation days
 
    for agt in range(0,var.numAgents):    
        fileOut = open("recoveryStates_agt"+str(agt)+".csv","w")
        for h in range(0,var.hoursInDay):
            var.agentsQ[agt].numClustersTracker[h] = {}
            var.agentsQ[agt].dictClusterObjects[h] = {}
            for act in var.agentsQ[agt].actionPhases:
                if(len(stateData[agt][h][act]) != 0):
                    var.agentsQ[agt].numClustersTracker[h][act] = int(sum(np.std(stateData[agt][h][act], axis = 0)))
                    if(var.agentsQ[agt].numClustersTracker[h][act] > len(stateData[agt][h][act])):
                        var.agentsQ[agt].numClustersTracker[h][act] = len(stateData[agt][h][act])
                    print('------- Number of clusters -------')
                    print('agent = ' + str(agt))
                    print('h = ', h)
                    print('action = ', act)
                    print('numClustersTracker[h][act] = ', var.agentsQ[agt].numClustersTracker[h][act])
                    
                    var.agentsQ[agt].dictClusterObjects[h][act] = KMeans(n_clusters = var.agentsQ[agt].numClustersTracker[h][act])                    
                    var.agentsQ[agt].dictClusterObjects[h][act].fit(stateData[agt][h][act]) 
                    coord = var.agentsQ[agt].dictClusterObjects[h][act].cluster_centers_
                    for k in range(0,var.agentsQ[agt].numClustersTracker[h][act]):
                        fileOut.write(str(h) + "  "  + str(act))
                        map(lambda y: fileOut.write("  " + str(y)), coord[k])
                        fileOut.write("\n")
                else:
                    print('\n ERROR: Missing data for h:'+str(h)+' (act):'+str(act) + 'for agent '+str(agt))
        fileOut.close() 
            
        
    for sl in var.SLs:        
        totalClusters = 0;
        for h in range(var.hoursInDay): 
            for act in var.agentsQ[sl].actionPhases:
                totalClusters += var.agentsQ[sl].numClustersTracker[h][act]
        print('agent ' + str(sl)  + ' ---> totalClusters = ' + str(totalClusters))
        var.agentsQ[sl].numStates = totalClusters
    
    for sl in var.SLs:        
        stateCounter = 0
        for h in range(var.hoursInDay): 
            var.agentsQ[sl].mapDiscreteStates[h] = {}
            for act in var.agentsQ[sl].actionPhases:
                var.agentsQ[sl].mapDiscreteStates[h][act] = {}
                for c in range(var.agentsQ[sl].numClustersTracker[h][act]):
                    var.agentsQ[sl].mapDiscreteStates[h][act][c] = stateCounter
                    stateCounter += 1

    for sl in var.SLs:
        filename_numpy = f'./models/map_agentQ{sl}.pkl'
        pickle.dump(var.agentsQ[sl].mapDiscreteStates, open(filename_numpy, 'wb'))       
        for h in range(var.hoursInDay):
            for act in var.agentsQ[sl].actionPhases:
                filename_model = f'./models/model_agentQ{sl}_h{h}_act{act}.sav'                
                pickle.dump(var.agentsQ[sl].dictClusterObjects[h][act], open(filename_model, 'wb'))                
                                
                #aa = pickle.load(open('file.pkl', 'rb'))

                        
def writeDataClusters():
    dfClusters = pd.DataFrame()
    for agt in range(var.numAgents):        
        for h in range(var.hoursInDay):
            aux = [agt]
            aux.append(h)
            for act in var.agentsQ[agt].actionPhases:
                aux.append(var.agentsQ[agt].numClustersTracker[h][act])
            df = pd.DataFrame([aux])
            dfClusters = dfClusters.append(df, ignore_index=True) 
    aux = ['agt', 'hour', 'F0', 'F1']
    dfClusters.columns = aux
    dfClusters.to_csv('dfClusters.csv')
            
 