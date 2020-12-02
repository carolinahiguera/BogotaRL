'''
Created on 9/10/2016

@author: carolina
'''
import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

import subprocess
import traci
import random
import pandas as pd
import numpy as np
import math

import var
import arrivalRateGen

sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData
FIFO = '/tmp/sumo_tf'

GUI = True

def loadData():
    df=pd.DataFrame.from_csv('./data_org/dfQueue_testTF_int0_day0.csv')
    timeBase = df.values[:,0]*(1.0*var.secondsInHour)
    samples = df.shape[0]
    dataQueues = {}; dataTimes = {}; dataSpeed = {}
    for v in var.Vertex:
        edges = len(var.vertexAgents[v].listEdges)
        dataQueues[v] = np.zeros([samples, edges]) 
        dataTimes[v] = np.zeros([samples, edges]) 
        dataSpeed[v] = np.zeros([samples, edges]) 
    
        for day in range(var.totalDaysTest-1):
            df=pd.DataFrame.from_csv(f'./data_org/dfQueue_testTF_int{v}_day{day}.csv')
            dataQ = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfWaiting_testTF_int{v}_day{day}.csv')
            dataW = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfSpeed_testTF_int{v}_day{day}.csv')
            dataS = df.values
            for e in range(edges):
                dataQueues[v][:,e] += dataQ[:,e+1] #en veh
                dataTimes[v][:,e] += dataW[:,e+1] #en minutos
                dataSpeed[v][:,e] += dataS[:,e+1] #en m/s
    return timeBase, dataQueues, dataTimes, dataSpeed

def getTravelTimes(dfQueueTracker, dfWaitingTracker, dfSpeedTracker):
    global timeBase, dataQueues, dataTimes, dataSpeed
    travel_times = np.zeros([len(var.routes)])
    for r in range(len(var.routes)):
        for i in range(len(var.routes[r]['route_agents'])):
            agent = var.routes[r]['route_agents'][i]
            edge_name = var.routes[r]['route_edge'][i]            
            edge = var.vertexAgents[agent].listEdges.index(edge_name)+1

            # x = np.array(dfQueueTracker[agent]).shape[0]
            # avg_mask = np.ones(var.WINDOW) / var.WINDOW
            # queue = dataQueues[agent][:,edge-1]/5.0
            # queue = np.convolve(queue, avg_mask, 'same')
            # time = dataTimes[agent][:,edge-1]/5.0
            # time = np.convolve(time, avg_mask, 'same')
            # speed = dataSpeed[agent][:,edge-1]/5.0
            # speed = np.convolve(speed, avg_mask, 'same')

            # numVeh = queue[900+x-1]
            # waitTime = time[900+x-1]/numVeh if numVeh>0 else 0.0
            # vel = speed[900+x-1]

            x = np.array(dfQueueTracker[agent]).shape[0]          
            queue = np.array(dfQueueTracker[agent])[:,edge] + dataQueues[agent][900:900+x,edge-1]
            queue = queue / 5.0
            time = np.array(dfWaitingTracker[agent])[:,edge] + dataTimes[agent][900:900+x,edge-1]
            time = time / 5.0
            speed = np.array(dfSpeedTracker[agent])[:,edge] + dataSpeed[agent][900:900+x,edge-1]
            speed = speed / 5.0

            if x < var.WINDOW:
                numVeh = np.mean(queue)
                waitTime = np.mean(time)/numVeh if numVeh>0 else 0.0
                vel = np.mean(speed)
            else:
                numVeh = np.mean(queue[x-var.WINDOW:x])
                waitTime = np.mean(time[x-var.WINDOW:x])/numVeh if numVeh>0 else 0.0
                vel = np.mean(speed[x-var.WINDOW:x])

            # x = np.array(dfQueueTracker[agent]).shape[0]
            # if x < var.WINDOW:
            #     queue = np.array(dfQueueTracker[agent])[:,edge] + dataQueues[agent][0:x,edge-1]
            #     queue = queue / 5.0
            #     time = np.array(dfWaitingTracker[agent])[:,edge] + dataTimes[agent][0:x,edge-1]
            #     time = time / 5.0
            #     speed = np.array(dfSpeedTracker[agent])[:,edge] + dataSpeed[agent][0:x,edge-1]
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

            length = var.vertexAgents[agent].lengthEdges[edge-1]
            if vel < 1.0:
                travel_times[r] += waitTime
            else:
                travel_times[r] += waitTime + (length/vel)/60.0
    #print(travel_times)
    return travel_times


#arrivalRateGen.createPolyFlow()
timeBase, dataQueues, dataTimes, dataSpeed = loadData()
#Inicio prueba TF
inYellow = False
secInYellow = 0
tiemposViaje = np.empty([0,4])

for day in range(var.totalDaysTest):
    fileOut = open("days.csv","w")
    fileOut.write(str(day)+"\n")
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
    dfActions = pd.DataFrame()
    
    for v in var.Vertex:        
        dfRewVals[v] = pd.DataFrame()
        dfQueueTracker[v] = pd.DataFrame()
        dfWaitingTracker[v] = pd.DataFrame() 
        dfC02Emission[v] = pd.DataFrame()
        dfFuelConsumption[v] = pd.DataFrame()
        dfNOxEmission[v] = pd.DataFrame()
        dfNoiseEmission[v] = pd.DataFrame()
        dfSpeedTracker[v] = pd.DataFrame() 
    
    currHod = 0
    currSod = 0
    lastTravelTime = np.zeros(len(var.routes))
    
    
    while currSod < var.secondsInDay: 
        if currHod != currSod/var.secondsInHour:
            currHod = int(currSod/var.secondsInHour)
            #print('    testing day = ', day)
            #print('    hour = ', currHod)
               
        
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
                    var.vertexAgents[v].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))/60.0
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
                
                # ================ C02 emmissions in mg
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:
                    aux.append(traci.edge.getCO2Emission(str(edge)))
                df = pd.DataFrame([aux])
                dfC02Emission[v] = dfC02Emission[v].append(df, ignore_index=True)
                
                # ================ NOx emmissions in mg
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getNOxEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNOxEmission[v] = dfNOxEmission[v].append(df, ignore_index=True)
                
                # ================ fuel consumption in ml 
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getFuelConsumption(str(edge)))
                df = pd.DataFrame([aux])
                dfFuelConsumption[v] = dfFuelConsumption[v].append(df, ignore_index=True)
                
                # ================ noise emission in db 
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getNoiseEmission(str(edge)))
                df = pd.DataFrame([aux])
                dfNoiseEmission[v] = dfNoiseEmission[v].append(df, ignore_index=True)

                # ================ speed in m/s
                aux = [currSod]
                for edge in var.vertexAgents[v].listEdges:                        
                    aux.append(traci.edge.getLastStepMeanSpeed(str(edge)))
                df = pd.DataFrame([aux])
                dfSpeedTracker[v] = dfSpeedTracker[v].append(df, ignore_index=True)
            
                #Update reward of each vertex agent and save its information
                var.vertexAgents[v].updateReward()
                df = pd.DataFrame([[currSod, var.vertexAgents[v].currReward]])
                dfRewVals[v] = dfRewVals[v].append(df, ignore_index=True)

            lastTravelTime = getTravelTimes(dfQueueTracker, dfWaitingTracker, dfSpeedTracker)
            
                            
        #Save sequence of actions taken by vertex agents
        data = SumoData()
        data.time_stamp = currSod
        #aux = [currSod]
        for v in var.Vertex:
            phase = int(traci.trafficlight.getPhase(str(v)))
            action = data.action.add()
            action.agent_id = v
            action.action = phase
            speed = data.mean_speed.add()
            x = np.array(dfSpeedTracker[v]).shape[0]-1
            vel = np.array(dfSpeedTracker[v])[x,1:]
            speed.agent_id = v
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
    traci.close() #End on day of simulation
    #np.save('travel_times3.npy', tiemposViaje)

    #Save traffic information for each vertex Agent
    # for v in var.Vertex:
    #     colNames = ['hour']
    #     for edge in var.vertexAgents[v].listEdges:
    #         colNames.append(edge)
        
    #     dfQueueTracker[v].columns = colNames
    #     dfQueueTracker[v]['hour'] = dfQueueTracker[v]['hour']/(1.0*var.secondsInHour)
    #     dfQueueTracker[v].to_csv('./data/dfQueue_testTF_int' + str(v) + '_day' + str(day) + '.csv')
        
    #     dfWaitingTracker[v].columns = colNames
    #     dfWaitingTracker[v]['hour'] = dfWaitingTracker[v]['hour']/(1.0*var.secondsInHour)
    #     dfWaitingTracker[v].to_csv('./data/dfWaiting_testTF_int' + str(v) + '_day' + str(day) + '.csv')
    
    #     dfSpeedTracker[v].columns = colNames
    #     dfSpeedTracker[v]['hour'] = dfSpeedTracker[v]['hour']/(1.0*var.secondsInHour)
    #     dfSpeedTracker[v].to_csv('./data/dfSpeed_testTF_int' + str(v) + '_day' + str(day) + '.csv')
    
    # 