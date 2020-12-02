'''
Created on 3/10/2016

@author: carolina
'''
import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

import subprocess
from var import lastDay
import traci
import random
import pandas as pd
import numpy as np
import math

import var
#import arrivalRateGen

sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData
FIFO = '/tmp/sumo_indQ'

GUI = True

def loadData():
    df=pd.DataFrame.from_csv('./data_org/dfQueue_test_agt0_day0.csv')
    timeBase = df.values[:,0]*(1.0*var.secondsInHour)
    samples = df.shape[0]
    dataQueues = {}; dataTimes = {}; dataSpeed = {}
    for v in var.SLs:
        edges = len(var.agents[v].listEdges)
        dataQueues[v] = np.zeros([samples, edges]) 
        dataTimes[v] = np.zeros([samples, edges]) 
        dataSpeed[v] = np.zeros([samples, edges]) 
    
        for day in range(var.totalDaysTest-1):
            df=pd.DataFrame.from_csv(f'./data_org/dfQueue_test_agt{v}_day{day}.csv')
            dataQ = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfWaiting_test_agt{v}_day{day}.csv')
            dataW = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfMeanSpeed_test_agt{v}_day{day}.csv')
            dataS = df.values
            for e in range(edges):
                dataQueues[v][:,e] += dataQ[:,e+1] #en veh
                dataTimes[v][:,e] += dataW[:,e+1] #en minutos
                dataSpeed[v][:,e] += dataS[:,e+1] #en m/s
    return timeBase, dataQueues, dataTimes, dataSpeed


def getTravelTimes(dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dataQueues, dataTimes, dataSpeed):
    travel_times = np.zeros([len(var.routes)])
    for r in range(len(var.routes)):
        for i in range(len(var.routes[r]['route_agents'])):
            agent = var.routes[r]['route_agents'][i]
            edge_name = var.routes[r]['route_edge'][i]            
            edge = var.agents[agent].listEdges.index(edge_name)+1
            x = np.array(dfQueueTracker[agent]).shape[0]

            # avg_mask = np.ones(var.WINDOW) / var.WINDOW
            # queue = dataQueues[agent][:,edge-1]/5.0
            # queue = np.convolve(queue, avg_mask, 'same')
            # time = dataTimes[agent][:,edge-1]/5.0
            # time = np.convolve(time, avg_mask, 'same')
            # speed = dataSpeed[agent][:,edge-1]/5.0
            # speed = np.convolve(speed, avg_mask, 'same')

            # numVeh = queue[120+x-1]
            # waitTime = time[120+x-1]/numVeh if numVeh>0 else 0.0
            # vel = speed[120+x-1]

            queue = np.array(dfQueueTracker[agent])[:,edge] + dataQueues[agent][120:120+x,edge-1]
            queue = queue / 5.0
            time = np.array(dfWaitingTracker[agent])[:,edge] + dataTimes[agent][120:120+x,edge-1]
            time = time / 5.0
            speed = np.array(dfSpeedTracker[agent])[:,edge] + dataSpeed[agent][120:120+x,edge-1]
            speed = speed / 5.0

            if x < var.WINDOW:
                numVeh = np.mean(queue)
                waitTime = np.mean(time)/numVeh if numVeh>0 else 0.0
                vel = np.mean(speed)
            else:
                numVeh = np.mean(queue[x-var.WINDOW:x])
                waitTime = np.mean(time[x-var.WINDOW:x])/numVeh if numVeh>0 else 0.0
                vel = np.mean(speed[x-var.WINDOW:x])


            # if x < var.WINDOW:
            #     queue = np.array(dfQueueTracker[agent])[:,edge] + dataQueues[agent][0:x,edge-1]
            #     queue = queue / 5.0
            #     time = np.array(dfWaitingTracker[agent])[:,edge] + dataTimes[agent][0:x,edge-1]
            #     time = time / 5.0
            #     speed = np.array(dfSpeedTracker[agent])[:,edge] + dataSpeed[agent][0:x,edge-1]
            #     speed = speed / 5.0
            #     numVeh = np.mean(queue)
            #     waitTime = np.mean(time)/numVeh if numVeh>0 else 0.0
            #     vel = np.mean(speed)
            #     # numVeh = queue[-1]
            #     # waitTime = time[-1]/numVeh if numVeh>0 else 0.0
            #     # vel = speed[-1]
            # else:
            #     queue = np.array(dfQueueTracker[agent])[:,edge] + dataQueues[agent][0:x,edge-1]
            #     queue = queue / 5.0
            #     time = np.array(dfWaitingTracker[agent])[:,edge] + dataTimes[agent][0:x,edge-1]
            #     time = time / 5.0
            #     speed = np.array(dfSpeedTracker[agent])[:,edge] + dataSpeed[agent][0:x,edge-1]
            #     speed = speed / 5.0

            #     avg_mask = np.ones(var.WINDOW) / var.WINDOW
            #     queue = np.convolve(queue, avg_mask, 'same')
            #     time = np.convolve(time, avg_mask, 'same')
            #     speed = np.convolve(speed, avg_mask, 'same')
            #     numVeh = np.mean(queue[len(queue)-var.WINDOW:len(queue)])
            #     waitTime = np.mean(time[len(time)-var.WINDOW:len(time)])/numVeh if numVeh>0 else 0.0
            #     vel = np.mean(speed[len(speed)-var.WINDOW:len(speed)])

            length = var.agents[agent].lengthEdges[edge-1]
            if vel < 1.0:
                travel_times[r] += waitTime
            else:
                travel_times[r] += waitTime + (length/vel)/60.0
    #print(travel_times)
    return travel_times


def test(dayLoad):
    inYellow = False
    secInYellow = 0
    tiemposViaje = np.empty([0,4])
    timeBase, dataQueues, dataTimes, dataSpeed = loadData()
    
    for sl in var.SLs:
        var.agents[sl].loadKnowledge(dayLoad-1)
    
    for day in range(var.totalDaysTest):

        fileOut = open("days.csv","w")
        fileOut.write("Testing day: "+str(day)+"\n")
        fileOut.close()

        print(("Testing day: "+str(day)))
        #arrivalRateGen.writeRoutes(day+1)
        projectName = var.project + ".sumocfg"

        if GUI:
            traci.start(['sumo-gui', "-c", projectName, '-g', 'gui-set.xml']) 
        else:
            traci.start(['sumo', "-c", projectName]) 

        # sumoProcess = subprocess.Popen([f'/home/{user}/programs/sumo-0.27.1/bin/sumo-gui', "-c", projectName, \
        #         "--remote-port", str(var.PORT)], stdout=sys.stdout, stderr=sys.stderr) 
        # traci.init(var.PORT)
        
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
        lastTravelTime = np.zeros(len(var.routes))
        lastTraciPhase = np.zeros(len(var.agents))
        for sl in var.SLs:
            lastTraciPhase[sl] = int(traci.trafficlight.getPhase(str(sl)))

        #============== BEGIN A DAY
        while currSod < var.secondsInDay: 
            if currHod != currSod/var.secondsInHour:
                currHod = int(currSod/var.secondsInHour)
                #print('    testing day = ', day)
                #print('    hour = ', currHod)
            
            if(inYellow): #Check duration of yellow phase                
                if(secInYellow >= var.minTimeInYellow):
                    secInYellow = 0
                    inYellow = False
                    for sl in var.SLs:
                        if(var.agents[sl].currPhaseID != var.agents[sl].newPhaseID):
                            traci.trafficlight.setPhase(str(sl),var.agents[sl].newPhaseID)                            
                            var.agents[sl].currPhaseID = var.agents[sl].newPhaseID
                            lastTraciPhase[sl] = var.agents[sl].currPhaseID
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
                        var.agents[sl].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60.0
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
                    var.agents[sl].update()
                
                #Save sequence of actions taken by agents
                aux = [currSod]
                for sl in var.SLs:
                    aux.append(var.agents[sl].newPhaseID)
                df = pd.DataFrame([aux])
                dfActions = dfActions.append(df, ignore_index=True)

                #travel_times = getTravelTimes(dfQueueTracker, dfWaitingTracker, dfSpeedTracker)
                #tiemposViaje = np.append(tiemposViaje, [travel_times], axis=0)

                #=========== APPLY NEW PHASES
                for sl in var.SLs:
                    if(var.agents[sl].currPhaseID == var.agents[sl].newPhaseID): #extend current phase
                        traci.trafficlight.setPhase(str(sl),var.agents[sl].newPhaseID)                        
                        lastTraciPhase[sl] = var.agents[sl].newPhaseID
                    else: #change to new phase
                        currPhase = var.agents[sl].actionPhases.index(var.agents[sl].currPhaseID)
                        newPhase = var.agents[sl].actionPhases.index(var.agents[sl].newPhaseID)
                        auxPhase = var.agents[sl].auxPhases[currPhase][newPhase]
                        traci.trafficlight.setPhase(str(sl), auxPhase)                        
                        inYellow = True
                        lastTraciPhase[sl] = auxPhase

                lastTravelTime = getTravelTimes(dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dataQueues, dataTimes, dataSpeed)
                        
            #Save sequence of actions taken by vertex agents
            data = SumoData()
            data.time_stamp = currSod
            #aux = [currSod]
            for sl in var.SLs:
                #phase = int(traci.trafficlight.getPhase(str(sl)))
                phase = int(lastTraciPhase[sl])
                action = data.action.add()
                action.agent_id = sl
                action.action = phase
                speed = data.mean_speed.add()
                x = np.array(dfSpeedTracker[sl]).shape[0]-1
                vel = np.array(dfSpeedTracker[sl])[x,1:]
                speed.agent_id = sl
                speed.speed.extend(vel)
            #    aux.append(phase)
            #travel_times = getTravelTimes()
            data.travel_times.extend(lastTravelTime)
            #df = pd.DataFrame([aux])
            #dfActions = dfActions.append(df, ignore_index=True)        
            #tiemposViaje = np.append(tiemposViaje, [travel_times], axis=0)         
                
                        
            #print('Escribiendo datos de tiempos de viaje')
            fifo = open(FIFO, 'rb')
            fifo.read()
            fifo.close()
            fifo = open(FIFO, 'wb')
            fifo.write(data.SerializeToString())
            fifo.close()
            #print('Finalizado')

            currSod += 1
            traci.simulationStep() 
        traci.close() #End one day of simulation
        #np.save('travel_times3.npy', tiemposViaje)

        #Save traffic information for each Agent
        # for sl in var.SLs:
        #     colNames = ['hour']
        #     for edge in var.agents[sl].listEdges:
        #         colNames.append(edge)
                
        #     dfQueueTracker[sl].columns = colNames
        #     dfQueueTracker[sl]['hour'] = dfQueueTracker[sl]['hour']/(1.0*var.secondsInHour)
        #     dfQueueTracker[sl].to_csv('./data/dfQueue_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
        #     dfWaitingTracker[sl].columns = colNames
        #     dfWaitingTracker[sl]['hour'] = dfWaitingTracker[sl]['hour']/(1.0*var.secondsInHour)
        #     dfWaitingTracker[sl].to_csv('./data/dfWaiting_test_agt' + str(sl) + '_day' + str(day) + '.csv')
            
        #     dfSpeedTracker[sl].columns = colNames
        #     dfSpeedTracker[sl]['hour'] = dfSpeedTracker[sl]['hour']/(1.0*var.secondsInHour)
        #     dfSpeedTracker[sl].to_csv('./data/dfSpeed_test_agt' + str(sl) + '_day' + str(day) + '.csv')
        # 