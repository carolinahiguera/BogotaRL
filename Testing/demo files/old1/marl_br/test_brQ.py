import os, sys
import subprocess
from var import lastDay
#sys.path.append("/Users/carolinaHiguera/Programas/sumo-0.27.1/tools")
sys.path.append("/home/carolina/programs/sumo-0.27.1/tools")
import traci
import random
import pandas as pd
import numpy as np
import math
import var
import arrivalRateGen
sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData

FIFO = '/tmp/sumo_brQ'
#os.mkfifo(FIFO)

def getTravelTimes():
    travel_times = np.zeros([len(var.routes)])
    for r in range(len(var.routes)):
        for i in range(len(var.routes[r]['route_agents'])):
            agent = var.routes[r]['route_agents'][i]
            edge_name = var.routes[r]['route_edge'][i]
            edge = var.agents[agent].listEdges.index(edge_name)+1

            num_veh = np.mean(np.array(dfQueueTracker[agent])[:,edge])
            waitTime = np.mean(np.array(dfWaitingTracker[agent])[:,edge])/num_veh if num_veh>0 else 0
            speed = np.mean(np.array(dfSpeedTracker[agent])[:,edge])

            # num_veh = np.mean(np.array(dfQueueTracker[agent])[-1,edge])
            # waitTime = np.mean(np.array(dfWaitingTracker[agent])[-1,edge])/num_veh if num_veh>0 else 0
            # speed = np.mean(np.array(dfSpeedTracker[agent])[-1,edge])

            # print(f'Agt:{agent},  Edge:{edge_name}, Speed:{speed}')
            # speed = np.mean(np.mean(np.array(dfSpeedTracker[agent])))
            length = var.agents[agent].lengthEdges[edge-1]
            if speed < 1.0:
                travel_times[r] += (waitTime)/60.0
            else:
                travel_times[r] += (waitTime + length/speed)/60
            #travel_times[r] += (waitTime/60.0 + length/speed) / 60.0
    return travel_times

#========================================

arrivalRateGen.createPolyFlow()

inYellow = False
secInYellow = 0

for sl in var.SLs:
    var.agents[sl].loadKnowledge(149)

for day in range(var.totalDaysTest):

    fileOut = open("days.csv","w")
    fileOut.write("Testing day: "+str(day)+"\n")
    fileOut.close()

    print("Testing day: "+str(day))
    arrivalRateGen.writeRoutes(day+1)
    projectName = "../miniCityQ/miniCity.sumocfg"

    sumoProcess = subprocess.Popen(['/home/carolina/programs/sumo-0.27.1/bin/sumo-gui', "-c", projectName, \
            "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
    traci.init(var.PORT)
    
    dfRewVals = {}
    dfQueueTracker = {}
    dfWaitingTracker = {}
    dfC02Emission = {}
    dfFuelConsumption = {}
    dfNOxEmission = {}
    dfNoiseEmission = {}
    dfSpeedTracker = {}
    dfEpsilon = pd.DataFrame()
    dfActions = pd.DataFrame()    
    for sl in var.SLs:        
        dfRewVals[sl] = pd.DataFrame()
        dfQueueTracker[sl] = pd.DataFrame()
        dfWaitingTracker[sl] = pd.DataFrame() 
        dfC02Emission[sl] = pd.DataFrame()
        dfFuelConsumption[sl] = pd.DataFrame()
        dfNOxEmission[sl] = pd.DataFrame()
        dfNoiseEmission[sl] = pd.DataFrame()
        dfSpeedTracker[sl] = pd.DataFrame()
    
    currHod = 0
    currSod = 0
    #============== BEGIN A DAY
    while currSod < var.secondsInDay: 
        if currHod != currSod/var.secondsInHour:
            currHod = int(currSod/var.secondsInHour)
            print( '    testing day = ', day)
            print( '    hour = ', currHod)
        
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
                
                # ================ C02 emmissions in mg
                aux = [currSod]
                for edge in var.agents[sl].listEdges:                        
                    aux.append(traci.edge.getCO2Emission(str(edge)))
                df = pd.DataFrame([aux])
                dfC02Emission[sl] = dfC02Emission[sl].append(df, ignore_index=True)
                
                # ================ NOx emmissions in mg
                aux = [currSod]
                for edge in var.agents[sl].listEdges:                        
                    aux.append(traci.edge.getNOxEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNOxEmission[sl] = dfNOxEmission[sl].append(df, ignore_index=True)
                
                # ================ fuel consumption in ml 
                aux = [currSod]
                for edge in var.agents[sl].listEdges:                        
                    aux.append(traci.edge.getFuelConsumption(str(edge)))
                df = pd.DataFrame([aux])
                dfFuelConsumption[sl] = dfFuelConsumption[sl].append(df, ignore_index=True)
                
                # ================ noise emission in db 
                aux = [currSod]
                for edge in var.agents[sl].listEdges:                        
                    aux.append(traci.edge.getNoiseEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNoiseEmission[sl] = dfNoiseEmission[sl].append(df, ignore_index=True)

                # ================ mean speed
                aux = [currSod]
                for edge in var.agents[sl].listEdges:                        
                    aux.append(traci.edge.getLastStepMeanSpeed(str(edge)))
                df = pd.DataFrame([aux])
                dfSpeedTracker[sl] = dfSpeedTracker[sl].append(df, ignore_index=True)
            
                #Update reward of each agent and save its information
                var.agents[sl].updateReward()
                df = pd.DataFrame([[currSod, var.agents[sl].currReward]])
                dfRewVals[sl] = dfRewVals[sl].append(df, ignore_index=True)
            
            #=========== APPLY LEARNING FOR EACH AGENTS
            for sl in var.SLs:
                var.agents[sl].followPolicy(currHod)
            #update joint actions
            for sl in var.SLs:
                var.agents[sl].updateJointAaction()
            
            #Save sequence of actions taken by agents
            aux = [currSod]
            for sl in var.SLs:
                aux.append(var.agents[sl].newPhaseID)
            df = pd.DataFrame([aux])
            dfActions = dfActions.append(df, ignore_index=True)

            #travel times
            travel_times = getTravelTimes()
            
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
        
        #send proto
        data = SumoData()
        data.time_stamp = currSod
        if len(travel_times) != 0:
            data.travel_times.extend(travel_times)
        for sl in var.SLs:
            action = data.action.add()
            action.agent_id = sl
            action.action = var.agents[sl].actionPhases.index(var.agents[sl].currPhaseID)

        print('Escribiendo datos de tiempos de viaje')
        fifo = open(FIFO, 'rb')
        fifo.read()
        fifo.close()
        fifo = open(FIFO, 'wb')
        fifo.write(data.SerializeToString())
        fifo.close()
        print('Finalizado')            
        
        currSod += 1
        traci.simulationStep() 
    traci.close() #End one day of simulation