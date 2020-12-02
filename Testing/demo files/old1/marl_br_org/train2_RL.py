'''
Created on 3/10/2016

@author: ubuntu
'''
import os, sys
import subprocess
from var import lastDay
#sys.path.append("/Users/ubuntuHiguera/Programas/sumo-0.27.1/tools")
sys.path.append("/home/ubuntu/Programas/sumo-0.27.1/tools")
import traci
import random
import pandas as pd
import numpy as np
import math

import var
import arrivalRateGen

def train():
    inYellow = False
    secInYellow = 0
    
    for sl in var.SLs:
        if(var.lastDay==-1):
            var.agents[sl].initAgent()
        else:
            var.agents[sl].loadKnowledge(var.lastDay)
    
    for day in range(var.lastDay+1, var.totalDaysTrain):

        fileOut = open("days.csv","w")
        fileOut.write("Training day: "+str(day)+"\n")
        fileOut.close()

        print("Training day: "+str(day))
        arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + ".sumocfg"
    
        sumoProcess = subprocess.Popen(['/home/ubuntu/Programas/sumo-0.27.1/bin/sumo', "-c", projectName, \
                "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        traci.init(var.PORT)
        
        dfRewVals = {}
        dfQueueTracker = {}
        dfWaitingTracker = {}
        dfEpsilon = pd.DataFrame()
        dfActions = pd.DataFrame()
        
        for sl in var.SLs:        
            dfRewVals[sl] = pd.DataFrame()
            dfQueueTracker[sl] = pd.DataFrame()
            dfWaitingTracker[sl] = pd.DataFrame()             
        
        currHod = 0
        currSod = 0
        #============== BEGIN A DAY
        while currSod < var.secondsInDay: 
            if currHod != currSod/var.secondsInHour:
                currHod = int(currSod/var.secondsInHour)
                print '    training day = ', day
                print '    hour = ', currHod
            
            if(inYellow): #Check duration of yellow phase                
                if(secInYellow >= var.minTimeInYellow):
                    secInYellow = 0
                    inYellow = False
                    for sl in var.SLs:
                        if(var.agents[sl].currPhaseID != var.agents[sl].newPhaseID):
                            traci.trafficlights.setPhase(str(sl),var.agents[sl].newPhaseID)                            
                            var.agents[sl].currPhaseID = var.agents[sl].newPhaseID
                secInYellow += 1
                            
            #============== MAKE A COLLECTIVE DECISION
            if(currSod%(var.minTimeInYellow + var.minTimeInGreen) == 0):
                
                #=========== UPDATE INFORMATION OF ALL AGENTS
                for sl in var.SLs:
                    #================= count halted vehicles (4 elements)
                    for lane in var.agents[sl].listLanes:
                        var.agents[sl].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
                    idx = 0
                    for edge in var.agents[sl].listEdges:
                        var.agents[sl].queueTracker[edge] = 0
                        for lane in range(var.agents[sl].numberLanes[idx]):
                            var.agents[sl].queueTracker[edge] += var.agents[sl].laneQueueTracker[str(edge) + '_' + str(lane)]
                        idx += 1
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:
                        aux.append(var.agents[sl].queueTracker[edge])
                    df = pd.DataFrame([aux])
                    dfQueueTracker[sl] = dfQueueTracker[sl].append(df, ignore_index=True)                     
                    
                    # ================ cum waiting time in minutes
                    for lane in var.agents[sl].listLanes:
                        var.agents[sl].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60
                    idx = 0;
                    for edge in var.agents[sl].listEdges:
                        var.agents[sl].waitingTracker[edge] = 0
                        for lane in range(var.agents[sl].numberLanes[idx]):
                            var.agents[sl].waitingTracker[edge] += var.agents[sl].laneWaitingTracker[str(edge) + '_' + str(lane)]
                        idx += 1 
                    aux = [currSod]
                    for edge in var.agents[sl].listEdges:
                        aux.append(var.agents[sl].waitingTracker[edge])
                    df = pd.DataFrame([aux])
                    dfWaitingTracker[sl] = dfWaitingTracker[sl].append(df, ignore_index=True)
                
                    #Update reward of each agent and save its information
                    var.agents[sl].updateReward()
                    df = pd.DataFrame([[currSod, var.agents[sl].currReward]])
                    dfRewVals[sl] = dfRewVals[sl].append(df, ignore_index=True)
                
                #=========== BEGIN LEARNING PROCESS FOR EACH AGENT
                for sl in var.SLs:
                    var.agents[sl].learnPolicy(day, currHod)
                #update joint actions
                for sl in var.SLs:
                    var.agents[sl].updateJointAaction()
                
                #Save epsilon values to verify exploration
                aux = [currSod]
                for sl in var.SLs:
                    aux.append(var.agents[sl].epsilon)
                df = pd.DataFrame([aux])
                dfEpsilon = dfEpsilon.append(df, ignore_index=True)
                
                #Save sequence of actions taken by agents
                aux = [currSod]
                for sl in var.SLs:
                    aux.append(var.agents[sl].newPhaseID)
                df = pd.DataFrame([aux])
                dfActions = dfActions.append(df, ignore_index=True)
                
                #=========== APPLY NEW PHASES
                for sl in var.SLs:
                    if(var.agents[sl].currPhaseID == var.agents[sl].newPhaseID): #extend current phase
                        traci.trafficlights.setPhase(str(sl),var.agents[sl].newPhaseID)                        
                    else: #change to new phase
                        currPhase = var.agents[sl].actionPhases.index(var.agents[sl].currPhaseID)
                        newPhase = var.agents[sl].actionPhases.index(var.agents[sl].newPhaseID)
                        auxPhase = var.agents[sl].auxPhases[currPhase][newPhase]
                        traci.trafficlights.setPhase(str(sl), auxPhase)                        
                        inYellow = True
                        
            currSod += 1
            traci.simulationStep() 
        traci.close() #End one day of simulation
        
        if(day==(var.lastDay+1)):
            dfRewValsSummaryMaster = {} 
            for sl in var.SLs:
                dfRewValsSummaryMaster[sl] = {}   
        
        #Save epsilon for each edge agent
        aux = ['hour']
        for sl in var.SLs:
            aux.append('agt_' + str(sl))
        dfEpsilon.columns = aux
        dfEpsilon['hour'] = dfEpsilon['hour']/(1.0*var.secondsInHour)
        dfEpsilon.to_csv('dfEpsilon_day'+str(day)+'.csv')
        
        #Save actions for each  agent
        aux = ['hour']
        for sl in var.SLs:
            aux.append('agt' + str(sl))
        dfActions.columns = aux
        dfActions['hour'] = dfActions['hour']/(1.0*var.secondsInHour)
        dfActions.to_csv('dfActions_train_day'+str(day)+'.csv')
        
        #Save reward information for each  agent
        for sl in var.SLs:
            dfRewVals[sl].columns = ['hour', 'day ' + str(day)]
            dfRewVals[sl]['hour'] = dfRewVals[sl]['hour']/(1.0*var.secondsInHour)
            dfRewVals[sl].to_csv('dfRewVals_train_agt'+str(sl)+'_day'+str(day)+'.csv')
            
            dfMean = dfRewVals[sl].mean(axis=0)
            dfMedian = dfRewVals[sl].median(axis = 0)
            dfMin = dfRewVals[sl].min(axis=0)
            df = pd.DataFrame([[str(day), dfMean[1], dfMedian[1], dfMin[1]]])
            df.columns = ['day', 'mean', 'median', 'min']
            
            if(day==(var.lastDay+1)):
                dfRewValsSummaryMaster[sl] = df
            else:
                dfRewValsSummaryMaster[sl] = dfRewValsSummaryMaster[sl].append(df, ignore_index=True)    
                dfRewValsSummaryMaster[sl].columns = ['day', 'mean', 'median', 'min']            
            dfRewValsSummaryMaster[sl].to_csv('dfRewValsSummary_train_agt' + str(sl) + '.csv')
        
        #Save traffic information for each Agent
        for sl in var.SLs:
            colNames = ['hour']
            for edge in var.agents[sl].listEdges:
                colNames.append(edge)
                
            dfQueueTracker[sl].columns = colNames
            dfQueueTracker[sl]['hour'] = dfQueueTracker[sl]['hour']/(1.0*var.secondsInHour)
            dfQueueTracker[sl].to_csv('dfQueue_train_agt' + str(sl) + '_day' + str(day) + '.csv')
            
            dfWaitingTracker[sl].columns = colNames
            dfWaitingTracker[sl]['hour'] = dfWaitingTracker[sl]['hour']/(1.0*var.secondsInHour)
            dfWaitingTracker[sl].to_csv('dfWaiting_train_agt' + str(sl) + '_day' + str(day) + '.csv')
        
        #Save learning for each edge agent
        for sl in var.SLs:
            var.agents[sl].saveLearning(day)
