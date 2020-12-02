'''
Created on 22/09/2016

@author: carolina
'''
import os, sys
import subprocess
#sys.path.append("/Users/carolinaHiguera/Programas/sumo-0.27.1/tools")
sys.path.append("/home/carolina/Programas/sumo-0.27.1/tools")
import traci
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sklearn
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import var
import arrivalRateGen

listMeanReward = []
listMedianReward = []
listMinReward = []

def computeReward(agtID, queueTracker, waitingTracker):
    reward = 0
    for key in var.agents[agtID].listEdges:
        reward -= ((var.agents[agtID].beta[0]*queueTracker[key])**var.agents[agtID].theta[0] + (var.agents[agtID].beta[1]*waitingTracker[key])**var.agents[agtID].theta[1]) 
    return reward

def learnDiscretization(daysToObserve):
    global listMeanReward, listMedianReward, listMinReward
    
    for sl in var.SLs:
        var.agents[sl].initAgent()
    
    stateData = {}
    for  n in range(var.numNeighbourPairs):
        stateData[n] = {}
        for h in range(var.hoursInDay):    
            stateData[n][h] = {}
            i = var.neighborsList[n][0]
            j = var.neighborsList[n][1]
            for ki_kj in range(var.agents[i].numActions[j]):
                stateData[n][h][ki_kj] =  np.array([])    
    
    
    for day in range(daysToObserve):

        fileOut = open("days.csv","w")
        fileOut.write("Observation day: "+str(day)+"\n")
        fileOut.close()

        # generate the random route schedule for the day
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + "-tf.sumo.cfg"
#         sumoProcess = subprocess.Popen(['/Users/carolinaHiguera/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
#                 "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        sumoProcess = subprocess.Popen(['/home/carolina/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
            "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr)

        traci.init(var.PORT)
        
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
                phase = var.agents[sl].planProgram[planName][idPhase]
                if(var.agents[sl].currPhaseID == phase and currSod != 0): # if phase HAS NOT changed
                    var.agents[sl].secsThisPhase += 1 # increase the seconds in the currentPhase 
                else: # IF THE PHASE HAS CHANGED
                    var.agents[sl].secsThisPhase = 0
                    var.agents[sl].currPhaseID = phase
            
            #end of yellow phase for some intersection?
            changePhase = [0 == (var.agents[sl].currPhaseID)%2 for sl in var.SLs]
            changeSec = [0 == var.agents[sl].secsThisPhase for sl in var.SLs]
            change = [1==changePhase[i]*changeSec[i] for i in var.SLs]
            
#             if(var.agents[0].currPhaseID==0 and var.agents[1].currPhaseID==0):
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
                    for lane in var.agents[agt].listLanes:
                        var.agents[agt].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.agents[agt].listEdges:
                        var.agents[agt].queueTracker[edge] = 0
                        for lane in range(var.agents[agt].numberLanes[idx]):
                            var.agents[agt].queueTracker[edge] += var.agents[agt].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    
                    # ================ cum waiting time in minutes
                    for lane in var.agents[agt].listLanes:
                        var.agents[agt].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.agents[agt].listEdges:
                        var.agents[agt].waitingTracker[edge] = 0
                        for lane in range(var.agents[agt].numberLanes[idx]):
                            var.agents[agt].waitingTracker[edge] += var.agents[agt].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    
                #============= UPDATE STATES FOR EACH NEIGHBOUR PAIR
                for agt in agentChanged:
                    nAgt = var.neighborsPerAgent[agt]
                    for nb in nAgt:
                        pair = var.neighborsList[nb]
                        stateDataEntry = []
                        for sl in pair:                        
                            for edge in var.agents[sl].listEdges:
                                stateDataEntry.append(var.agents[sl].queueTracker[edge])
                            for edge in var.agents[sl].listEdges:
                                stateDataEntry.append(var.agents[sl].waitingTracker[edge])
                        currJointAction = var.agents[pair[0]].getJointAction(pair[1])
                        if len(stateData[nb][hod][currJointAction]) == 0:
                            stateData[nb][hod][currJointAction] = np.array([stateDataEntry])
                        else:
                            stateData[nb][hod][currJointAction] = np.vstack([stateData[nb][hod][currJointAction], stateDataEntry])
                                             
                    # ================= track reward function
                    currRewValue = computeReward(agt, var.agents[agt].queueTracker, var.agents[agt].waitingTracker)
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
 
    for n in range(var.numNeighbourPairs):    
        i = var.neighborsList[n][0]
        j = var.neighborsList[n][1]
        fileOut = open("recoveryStates_"+str(i)+"_"+str(j)+".csv","w")
        for h in range(var.hoursInDay):
            var.agents[i].numClustersTracker[j][h] = {}
            var.agents[i].dictClusterObjects[j][h] = {}
            for ki_kj in range(var.agents[i].numActions[j]):
                if(len(stateData[n][h][ki_kj]) != 0):
                    var.agents[i].numClustersTracker[j][h][ki_kj] = int(sum(np.std(stateData[n][h][ki_kj], axis = 0)))
                    if(var.agents[i].numClustersTracker[j][h][ki_kj] > len(stateData[n][h][ki_kj])):
                        var.agents[i].numClustersTracker[j][h][ki_kj] = len(stateData[n][h][ki_kj])
                    print('------- Number of clusters -------')
                    print(('neigbours = [' + str(i) + ", " + str(j) + "]"))
                    print('h = ', h)
                    print('ki_kj = ', var.agents[i].jointActions[j][ki_kj])
                    print('numClustersTracker[j][h][ki_kj] = ', var.agents[i].numClustersTracker[j][h][ki_kj])
                    
                    var.agents[i].dictClusterObjects[j][h][ki_kj] = KMeans(n_clusters = var.agents[i].numClustersTracker[j][h][ki_kj])                    
                    var.agents[i].dictClusterObjects[j][h][ki_kj].fit(stateData[ n][h][ki_kj]) 
                    coord = var.agents[i].dictClusterObjects[j][h][ki_kj].cluster_centers_
                    for k in range(0,var.agents[i].numClustersTracker[j][h][ki_kj]):
                        fileOut.write(str(h) + "  "  + str(ki_kj))
                        list(map(lambda y: fileOut.write("  " + str(y)), coord[k]))
                        fileOut.write("\n")
                else:
                    print(('\n ERROR: Missing data for h:'+str(h)+' (ki_kj):'+str(var.agents[i].jointActions[j][ki_kj]) + 'for neighbour ['+str(i)+' - '+str(j)+']'))
        fileOut.close() 
            
        
    for sl in var.SLs:
        for n in var.agents[sl].neighbors:
            totalClusters = 0;
            for h in range(var.hoursInDay): 
                for ki_kj in range(var.agents[sl].numActions[n]):
                    totalClusters += var.agents[sl].numClustersTracker[n][h][ki_kj]
            print(('Pair(' + str(sl) + ', ' + str(n) + ') ---> totalClusters = ' + str(totalClusters)))
            var.agents[sl].numStates[n] = totalClusters
    
    for sl in var.SLs:
        for n in var.agents[sl].neighbors:
            stateCounter = 0
            for h in range(var.hoursInDay): 
                var.agents[sl].mapDiscreteStates[n][h] = {}
                for ki_kj in range(var.agents[sl].numActions[n]):
                    var.agents[sl].mapDiscreteStates[n][h][ki_kj] = {}
                    for c in range(var.agents[sl].numClustersTracker[n][h][ki_kj]):
                        var.agents[sl].mapDiscreteStates[n][h][ki_kj][c] = stateCounter
                        stateCounter += 1
                        
def writeDataClusters():
    dfClusters = pd.DataFrame()
    for n in range(var.numNeighbourPairs):        
        i = var.neighborsList[n][0]
        j = var.neighborsList[n][1]        
        for h in range(var.hoursInDay):
            aux = [i,j]
            aux.append(h)
            for ki_kj in range(var.agents[i].numActions[j]):
                aux.append(var.agents[i].numClustersTracker[j][h][ki_kj])
            df = pd.DataFrame([aux])
            dfClusters = dfClusters.append(df, ignore_index=True) 
    aux = ['agt_i', 'agt_j', 'hour', 'F0', 'F1', 'F2', 'F3']
    dfClusters.columns = aux
    dfClusters.to_csv('dfClusters.csv')
            

def plotClusterHistograms():
    dfClusters = {}
    for n in range(var.numNeighbourPairs):
        i = var.neighborsList[n][0]
        j = var.neighborsList[n][1]
        dfClusters[n] = pd.DataFrame.from_dict(var.agents[i].numClustersTracker[j], orient = 'index')
        colNames = []
        for ki_kj in range(var.agents[i].numActions[j]):
            colNames.append('Fase '+str(var.agents[i].jointActions[j][ki_kj]))
        dfClusters[i].columns = colNames
        dfClusters[i].plot(kind = 'bar', stacked = True)
        plt.xlabel('Hora')
        plt.ylabel('Numero de estados discretos escogidos')
        plt.title('(Agt_i: ' + str(i) + '- Agt_j: ' + str(j) + '): Estados discretos seleccionados por VQ para cada (hora, fase)')
        plt.show() 
