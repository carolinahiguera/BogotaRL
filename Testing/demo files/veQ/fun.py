'''
Created on 26/09/2016

@author: carolina
'''
'''
Created on 4/09/2016

@author: carolina
'''
import os, sys
import subprocess
#sys.path.append("/Users/CarolinaHiguera/Programas/sumo-0.27.1/tools")
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
    for key in var.vertexAgents[agtID].listEdges:
        reward -= ((var.vertexAgents[agtID].beta[0]*queueTracker[key])**var.vertexAgents[agtID].theta[0] + (var.vertexAgents[agtID].beta[1]*waitingTracker[key])**var.vertexAgents[agtID].theta[1]) 
    return reward

def learnDiscretization(daysToObserve):
    global listMeanReward, listMedianReward, listMinReward
    stateData = {}
    for e in range(var.numEdgeAgents):
        stateData[e] = {}
        for h in range(var.hoursInDay):    
            stateData[e][h] = {}
            for ki_kj in range(var.edgeAgents[e].numActions):
                stateData[e][h][ki_kj] = np.array([])
    
    for day in range(daysToObserve):
        # generate the random route schedule for the day
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + "-tf.sumo.cfg"
#         sumoProcess = subprocess.Popen(['/Users/CarolinaHiguera/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
#                 "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        sumoProcess = subprocess.Popen(['/home/carolina/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
            "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr)

        traci.init(var.PORT)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        
        for v in var.Vertex:        
            dfRewVals[v] = pd.DataFrame()
            dfQueueTracker[v] = pd.DataFrame()
            dfWaitingTracker[v] = pd.DataFrame()        
        
        hod = 0
        currSod = 0
                
        while currSod < var.secondsInDay:
            
            for v in var.Vertex:
                planName = traci.trafficlights.getProgram(str(v))
                idPhase = int(traci.trafficlights.getPhase(str(v)))
                phase = var.vertexAgents[v].planProgram[planName][idPhase]
                if(var.vertexAgents[v].currPhaseID == phase and currSod != 0): # if phase HAS NOT changed
                    var.vertexAgents[v].secsThisPhase += 1 # increase the seconds in the currentPhase 
                else: # IF THE PHASE HAS CHANGED
                    var.vertexAgents[v].secsThisPhase = 0
                    var.vertexAgents[v].currPhaseID = phase
            
            #end of yellow phase for some intersection?
            changePhase = [0 == (var.vertexAgents[v].currPhaseID)%2 for v in var.Vertex]
            changeSec = [0 == var.vertexAgents[v].secsThisPhase for v in var.Vertex]
            
            if (True in changePhase) and (True in changeSec):
                vertexChanged = [v for v in range(var.numVertexAgents) if((changePhase[v]*changeSec[v])==1)] #Vertex Agents ID who change phase
                
                #============  HOD
                if hod != currSod/var.secondsInHour:
                    hod = int(currSod/var.secondsInHour)
                    print 'observation day = ', day
                    print 'hour = ', hod
                
                #=========== UPDATE INFORMATION OF ALL VERTEX WHO CHANGED THEIR PHASE
                for v in vertexChanged:
                    #================= count halted vehicles (4 elements)
                    for lane in var.vertexAgents[v].listLanes:
                        var.vertexAgents[v].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.vertexAgents[v].listEdges:
                        var.vertexAgents[v].queueTracker[edge] = 0
                        for lane in range(var.vertexAgents[v].numberLanes[idx]):
                            var.vertexAgents[v].queueTracker[edge] += var.vertexAgents[v].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    
                    # ================ cum waiting time in minutes
                    for lane in var.vertexAgents[v].listLanes:
                        var.vertexAgents[v].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.vertexAgents[v].listEdges:
                        var.vertexAgents[v].waitingTracker[edge] = 0
                        for lane in range(var.vertexAgents[v].numberLanes[idx]):
                            var.vertexAgents[v].waitingTracker[edge] += var.vertexAgents[v].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                
                #============= UPDATE STATES FOR VERTEX'S EDGES
                for e in range(var.numEdgeAgents):
                    var.edgeAgents[e].updatedState = False
          
                for v in vertexChanged:
                    for e in var.v2e_agent[v]:
                        #================= Create and add state
                        stateDataEntry = []
                        for sl in var.edgeAgents[e].vertexAgt:
                            for edge in var.vertexAgents[sl].listEdges:
                                stateDataEntry.append(var.vertexAgents[sl].queueTracker[edge])
                            for edge in var.vertexAgents[sl].listEdges:
                                stateDataEntry.append(var.vertexAgents[sl].waitingTracker[edge])
                        currJointAction = var.edgeAgents[e].getJointAction()
                        if len(stateData[e][hod][currJointAction]) == 0:
                            stateData[e][hod][currJointAction] = np.array(stateDataEntry)
                        else:
                            stateData[e][hod][currJointAction] = np.vstack([stateData[e][hod][currJointAction], stateDataEntry])
                        var.edgeAgents[e].updatedState = True
                        
                    # ================= track reward function
                    currRewValue = computeReward(v, var.vertexAgents[v].queueTracker, var.vertexAgents[v].waitingTracker)
                    df = pd.DataFrame([[currSod, currRewValue]]) 
                    dfRewVals[v] = dfRewVals[v].append(df, ignore_index=True)
                    
            currSod += 1           
            traci.simulationStep()               
        traci.close() #End one day of observation
        
        aux = {}
        for i in range(0,3):
            aux[i] = []
        for v in var.Vertex:
            aux[0].append(dfRewVals[v].mean(axis = 0)[1])
            aux[1].append(dfRewVals[v].median(axis = 0)[1])
            aux[2].append(dfRewVals[v].min(axis = 0)[1])
        listMeanReward.append(aux[0])
        listMedianReward.append(aux[1])
        listMinReward.append(aux[2])
    
    #End of observation days
    for e in range(var.numEdgeAgents):
        fileOut = open("recoveryStates_edge"+str(e)+".csv","w")
        for h in range(var.hoursInDay): 
            var.edgeAgents[e].numClustersTracker[h] = {}
            var.edgeAgents[e].dictClusterObjects[h] = {}
            for ki_kj in range(var.edgeAgents[e].numActions):
                if(len(stateData[e][h][ki_kj]) != 0): 
                    var.edgeAgents[e].numClustersTracker[h][ki_kj] = int(sum(np.std(stateData[e][h][ki_kj], axis = 0)))
                    if(var.edgeAgents[e].numClustersTracker[h][ki_kj] > len(stateData[e][h][ki_kj])):
                        var.edgeAgents[e].numClustersTracker[h][ki_kj] = len(stateData[e][h][ki_kj])
                    print('------- Number of clusters -------')
                    print 'edge = ', var.Edges[e]
                    print 'h = ', h
                    print 'ki_kj = ', var.edgeAgents[e].jointActions[ki_kj]
                    print 'numClustersTracker[h][ki_kj] = ', var.edgeAgents[e].numClustersTracker[h][ki_kj]
                    
                    var.edgeAgents[e].dictClusterObjects[h][ki_kj] = KMeans(n_clusters = var.edgeAgents[e].numClustersTracker[h][ki_kj])
                    var.edgeAgents[e].dictClusterObjects[h][ki_kj].fit(stateData[e][h][ki_kj]) 
                    coord = var.edgeAgents[e].dictClusterObjects[h][ki_kj].cluster_centers_
                    for i in range(0,var.edgeAgents[e].numClustersTracker[h][ki_kj]):
                        fileOut.write(str(h) + "  "  + str(ki_kj))
                        map(lambda y: fileOut.write("  " + str(y)), coord[i])
                        fileOut.write("\n")
                else:
                    print('\n ERROR: Missing data for h:'+str(h)+' (ki_kj):'+str(var.edgeAgents[e].jointActions[ki_kj])+' edge: '+str(e))
        fileOut.close()    
        
    totalClusters = var.numEdgeAgents*[0]
    for e in range(0, var.numEdgeAgents):
        for h in range(var.hoursInDay): 
            for ki_kj in range(var.edgeAgents[e].numActions):
                totalClusters[e] += var.edgeAgents[e].numClustersTracker[h][ki_kj]
        print('Edge = ' + str(e) + ' - totalClusters = ' + str(totalClusters[e]))
        var.edgeAgents[e].numStates = totalClusters[e]  
    
    for e in range(0, var.numEdgeAgents):
        stateCounter = 0
        for h in range(var.hoursInDay): 
            var.edgeAgents[e].mapDiscreteStates[h] = {}
            for ki_kj in range(var.edgeAgents[e].numActions):
                var.edgeAgents[e].mapDiscreteStates[h][ki_kj] = {}
                for c in range(var.edgeAgents[e].numClustersTracker[h][ki_kj]):
                    var.edgeAgents[e].mapDiscreteStates[h][ki_kj][c] = stateCounter
                    stateCounter += 1
                    
def writeDataClusters():
    dfClusters = pd.DataFrame()
    for e in range(var.numEdgeAgents):        
        for h in range(var.hoursInDay):
            aux = [e]
            aux.append(h)
            for ki_kj in range(var.edgeAgents[e].numActions):
                aux.append(var.edgeAgents[e].numClustersTracker[h][ki_kj])
            df = pd.DataFrame([aux])
            dfClusters = dfClusters.append(df, ignore_index=True) 
    aux = ['edge', 'hour', 'F0', 'F1', 'F2', 'F3']
    dfClusters.columns = aux
    dfClusters.to_csv('dfClusters.csv')

def plotClusterHistograms():
    dfClusters = {}
    for e in range(0, var.numEdgeAgents):
        dfClusters[e] = pd.DataFrame.from_dict(var.edgeAgents[e].numClustersTracker, orient = 'index')
        colNames = []
        for ki_kj in range(var.edgeAgents[e].numActions):
            colNames.append('Fase '+str(var.edgeAgents[e].jointActions[ki_kj]))
        dfClusters[e].columns = colNames
        dfClusters[e].plot(kind = 'bar', stacked = True)
        plt.xlabel('Hora')
        plt.ylabel('Numero de estados discretos escogidos')
        plt.title('Edge '+ str(e) + ' (i' + str(var.edgeAgents[e].SL_i) + '_j' + str(var.edgeAgents[e].SL_j) + '): Estados discretos seleccionados por VQ para cada (hora, fase)')
        plt.show()  
                                
                        

