'''
Created on 3/10/2016

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
import math

import var
import arrivalRateGen
import variableElimination

def train():
    inYellow = False
    secInYellow = 0
    
    for e in range(var.numEdgeAgents):
        if(var.lastDay==-1):
            var.edgeAgents[e].initTables()
        else:
            var.edgeAgents[e].loadKnowledge(var.lastDay)
    for v in var.Vertex:
        var.vertexAgents[v].initAgent()
        
    fileOut = open("days.csv","w")
    
    for day in range(var.lastDay+1, var.totalDaysTrain):
        fileOut.write(str(day)+"\n")
        
        print("Training day: "+str(day))
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + ".sumocfg"
#         sumoProcess = subprocess.Popen(['/Users/CarolinaHiguera/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
#                 "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        
        sumoProcess = subprocess.Popen(['/home/carolina/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
                "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        traci.init(var.PORT)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        dfEpsilon = pd.DataFrame()
        dfActions = pd.DataFrame()
        
        for v in var.Vertex:        
            dfRewVals[v] = pd.DataFrame()
            dfQueueTracker[v] = pd.DataFrame()
            dfWaitingTracker[v] = pd.DataFrame() 
        
        currHod = 0
        currSod = 0
        
        while currSod < var.secondsInDay: 
            if currHod != currSod/var.secondsInHour:
                currHod = int(currSod/var.secondsInHour)
                print '    training day = ', day
                print '    hour = ', currHod
            
            if(inYellow): #Check duration of yellow phase
                secInYellow += 1
                if(secInYellow >= var.minTimeInYellow):
                    secInYellow = 0
                    inYellow = False
                    for v in var.Vertex:
                        if(var.vertexAgents[v].currPhaseID != var.vertexAgents[v].newPhaseID):
                            traci.trafficlights.setPhase(str(v),var.vertexAgents[v].newPhaseID)
                            var.vertexAgents[v].currPhaseID = var.vertexAgents[v].newPhaseID
            
            #============== IS TIME TO MAKE A COLLECTIVE DECISION?
            if(currSod%(var.minTimeInYellow + var.minTimeInGreen) == 0): 
                #=========== UPDATE INFORMATION OF ALL VERTEX AGENTS
                for v in var.Vertex:
                    #================= count halted vehicles (4 elements)
                    for lane in var.vertexAgents[v].listLanes:
                        var.vertexAgents[v].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.vertexAgents[v].listEdges:
                        var.vertexAgents[v].queueTracker[edge] = 0
                        for lane in range(var.vertexAgents[v].numberLanes[idx]):
                            var.vertexAgents[v].queueTracker[edge] += var.vertexAgents[v].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    aux = [currSod]
                    for edge in var.vertexAgents[v].listEdges:
                        aux.append(var.vertexAgents[v].queueTracker[edge])
                    df = pd.DataFrame([aux])
                    dfQueueTracker[v] = dfQueueTracker[v].append(df, ignore_index=True) 
                                        
                    # ================ cum waiting time in minutes
                    for lane in var.vertexAgents[v].listLanes:
                        var.vertexAgents[v].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.vertexAgents[v].listEdges:
                        var.vertexAgents[v].waitingTracker[edge] = 0
                        for lane in range(var.vertexAgents[v].numberLanes[idx]):
                            var.vertexAgents[v].waitingTracker[edge] += var.vertexAgents[v].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    aux = [currSod]
                    for edge in var.vertexAgents[v].listEdges:
                        aux.append(var.vertexAgents[v].waitingTracker[edge])
                    df = pd.DataFrame([aux])
                    dfWaitingTracker[v] = dfWaitingTracker[v].append(df, ignore_index=True)
                
                    #Update reward of each vertex agent and save its information
                    var.vertexAgents[v].updateReward()
                    df = pd.DataFrame([[currSod, var.vertexAgents[v].currReward]])
                    dfRewVals[v] = dfRewVals[v].append(df, ignore_index=True)
                
                #=========== BEGIN LEARNING PROCESS FOR EDGE AGENTS
                #update the states
                for e in range(var.numEdgeAgents):
                    var.edgeAgents[e].updateState(currHod)
                #get a*-->argmax Q(s',a') using max-plus algorithm
                variableElimination.Algorithm()
                #learn Policy
                for e in range(var.numEdgeAgents):
                    var.edgeAgents[e].learningPolicy(var.bestJointAction, day, currHod)
                #Save epsilon values to verify exploration
                aux = [currSod]
                for e in range(var.numEdgeAgents):
                    aux.append(var.edgeAgents[e].epsilon)
                df = pd.DataFrame([aux])
                dfEpsilon = dfEpsilon.append(df, ignore_index=True)
                #Save sequence of actions taken by vertex agents
                aux = [currSod]
                for v in var.Vertex:
                    aux.append(var.vertexAgents[v].newPhaseID)
                df = pd.DataFrame([aux])
                dfActions = dfActions.append(df, ignore_index=True)
                
                #Apply new phases
                for v in var.Vertex:
                    if(var.vertexAgents[v].currPhaseID == var.vertexAgents[v].newPhaseID): #extend current phase
                        traci.trafficlights.setPhase(str(v),var.vertexAgents[v].newPhaseID)                        
                    else: #change to new phase
                        currPhase = var.vertexAgents[v].actionPhases.index(var.vertexAgents[v].currPhaseID)
                        newPhase = var.vertexAgents[v].actionPhases.index(var.vertexAgents[v].newPhaseID)
                        auxPhase = var.vertexAgents[v].auxPhases[currPhase][newPhase]
                        traci.trafficlights.setPhase(str(v), auxPhase)
                        inYellow = True
                        
            currSod += 1
            traci.simulationStep() 
        traci.close() #End on day of simulation
        
        if(day==var.lastDay+1):
            dfRewValsSummaryMaster = {} 
            for v in var.Vertex:
                dfRewValsSummaryMaster[v] = {} 
        
        #Save epsilon for each edge agent
        aux = ['hour']
        for e in range(var.numEdgeAgents):
            aux.append('edge' + str(var.edgeAgents[e].SL_i) + '-' + str(var.edgeAgents[e].SL_j))
        dfEpsilon.columns = aux
        dfEpsilon['hour'] = dfEpsilon['hour']/(1.0*var.secondsInHour)
        dfEpsilon.to_csv('dfEpsilon_day'+str(day)+'.csv')
        
        #Save actions for each vertex agent
        aux = ['hour']
        for v in var.Vertex:
            aux.append('int' + str(var.vertexAgents[v].SL))
        dfActions.columns = aux
        dfActions['hour'] = dfActions['hour']/(1.0*var.secondsInHour)
        dfActions.to_csv('dfActions_train_day'+str(day)+'.csv')
        
        #Save reward information for each vertex agent
        for v in var.Vertex:
            dfRewVals[v].columns = ['hour', 'day ' + str(day)]
            dfRewVals[v]['hour'] = dfRewVals[v]['hour']/(1.0*var.secondsInHour)
            dfRewVals[v].to_csv('dfRewVals_train_int'+str(v)+'_day'+str(day)+'.csv')
            
            dfMean = dfRewVals[v].mean(axis=0)
            dfMedian = dfRewVals[v].median(axis = 0)
            dfMin = dfRewVals[v].min(axis=0)
            df = pd.DataFrame([[str(day), dfMean[1], dfMedian[1], dfMin[1]]])
            df.columns = ['day', 'mean', 'median', 'min']
            
            if day == 0:
                dfRewValsSummaryMaster[v] = df
            else:
                dfRewValsSummaryMaster[v] = dfRewValsSummaryMaster[v].append(df, ignore_index=True)    
                dfRewValsSummaryMaster[v].columns = ['day', 'mean', 'median', 'min']            
            dfRewValsSummaryMaster[v].to_csv('dfRewValsSummary_train_int' + str(v) + '.csv')
        
        #Save traffic information for each vertex Agent
        for v in var.Vertex:
            colNames = ['hour']
            for edge in var.vertexAgents[v].listEdges:
                colNames.append(edge)
            
            dfQueueTracker[v].columns = colNames
            dfQueueTracker[v]['hour'] = dfQueueTracker[v]['hour']/(1.0*var.secondsInHour)
            dfQueueTracker[v].to_csv('dfQueue_train_int' + str(v) + '_day' + str(day) + '.csv')
            
            dfWaitingTracker[v].columns = colNames
            dfWaitingTracker[v]['hour'] = dfWaitingTracker[v]['hour']/(1.0*var.secondsInHour)
            dfWaitingTracker[v].to_csv('dfWaiting_train_int' + str(v) + '_day' + str(day) + '.csv')
        
        #Save learning for each edge agent
        for e in range(var.numEdgeAgents):
            var.edgeAgents[e].saveLearning(day)
            
        fileOut.write("End training")
        fileOut.close()     