import os, sys
import subprocess
sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData

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
import FT.var as var

FIFO = '/tmp/sumo_tf'
# os.mkfifo(FIFO)

def getTrafficData(currSod):
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker
    for sl in range(var.num_agentsTF):
        v=sl
        for lane in var.agentsTF[sl].listLanes:
            var.agentsTF[sl].laneQueueTracker[lane] = traci.lane.getLastStepHaltingNumber(str(lane))
            var.agentsTF[sl].laneWaitingTracker[lane] = traci.lane.getWaitingTime(str(lane))
        idx = 0
        for edge in var.agentsTF[sl].listEdges:
            var.agentsTF[sl].queueTracker[edge] = 0
            var.agentsTF[sl].waitingTracker[edge] = 0
            for lane in range(var.agentsTF[sl].numberLanes[idx]):
                var.agentsTF[sl].queueTracker[edge] += var.agentsTF[sl].laneQueueTracker[str(edge) + '_' + str(lane)]
                var.agentsTF[sl].waitingTracker[edge] += var.agentsTF[sl].laneWaitingTracker[str(edge) + '_' + str(lane)]
            idx += 1
        for edge in var.agentsTF[v].listEdges:
            speed = traci.edge.getLastStepMeanSpeed(str(edge)) #m/s
            var.agentsTF[sl].speedTracker[edge] = speed
            #print(f'edge:{edge}, agent{sl}, speed: {speed}')
        aux_queue = [currSod]
        aux_waiting = [currSod]
        aux_speed = [currSod]
        for edge in var.agentsTF[v].listEdges:
            aux_queue.append(var.agentsTF[v].queueTracker[edge])
            aux_waiting.append(var.agentsTF[v].waitingTracker[edge])
            aux_speed.append(var.agentsTF[v].speedTracker[edge])
        #queue
        df = pd.DataFrame([aux_queue])
        dfQueueTracker[v] = dfQueueTracker[v].append(df, ignore_index=True)
        if len(dfQueueTracker[v]) > var.WINDOW:
            dfQueueTracker[v] = dfQueueTracker[v].drop(dfQueueTracker[v].index[0])
        #waiting time
        df = pd.DataFrame([aux_waiting])
        dfWaitingTracker[v] = dfWaitingTracker[v].append(df, ignore_index=True)
        if len(dfWaitingTracker[v]) > var.WINDOW:
            dfWaitingTracker[v] = dfWaitingTracker[v].drop(dfWaitingTracker[v].index[0])
        #speed
        df = pd.DataFrame([aux_speed])
        dfSpeedTracker[v] = dfSpeedTracker[v].append(df, ignore_index=True)
        if len(dfSpeedTracker[v]) > var.WINDOW:
            dfSpeedTracker[v] = dfSpeedTracker[v].drop(dfSpeedTracker[v].index[0])

        # save
        # dfQueueTracker[v].to_csv(f'./trackers/dfQueueTracker_agt{v}_{currSod}.csv', index=None, header=True)
        # dfWaitingTracker[v].to_csv(f'./trackers/dfWaitingTracker{v}_{currSod}.csv', index=None, header=True)
        # dfSpeedTracker[v].to_csv(f'./trackers/dfSpeedTracker{v}_{currSod}.csv', index=None, header=True)
    


def getActions(currSod):
    global dfActions, dfSeconds
    sec = [currSod]
    aux = [currSod]
    for v in range(var.num_agentsTF):
        aux.append(int(traci.trafficlights.getPhase(str(v))))
    df = pd.DataFrame([aux])
    dfActions = dfActions.append(df, ignore_index=True)
    df = pd.DataFrame([sec])
    dfSeconds = dfSeconds.append(df,  ignore_index=True)    
    return aux[1:len(aux)]  


def getTravelTimes():
    travel_times = np.zeros([len(var.routes)])
    for r in range(len(var.routes)):
        for i in range(len(var.routes[r]['route_agents'])):
            agent = var.routes[r]['route_agents'][i]
            edge_name = var.routes[r]['route_edge'][i]            
            edge = var.agentsTF[agent].listEdges.index(edge_name)+1
            num_veh = np.mean(np.array(dfQueueTracker[agent])[:,edge])
            waitTime = np.mean(np.array(dfWaitingTracker[agent])[:,edge])/num_veh if num_veh>0 else 0
            speed = np.mean(np.array(dfSpeedTracker[agent])[:,edge])                  
            length = var.agentsTF[agent].lengthEdges[edge-1]
            if speed < 1.0:
                travel_times[r] += (waitTime)/60.0
            else:
                travel_times[r] += (waitTime + length/speed)/60.0
            #travel_times[r] += (waitTime/60.0 + length/speed) / 60.0
    return travel_times






###------------ MAIN ---------------------
for day in range(var.totalDaysTest):
    # sumoCmd = [sumoBinary, "-c", "../miniCity/miniCity-tf.sumo.cfg", "--no-step-log", "true"]
    sumoProcess = subprocess.Popen([
        '/home/camilo/programs/sumo-0.27.1/bin/sumo-gui',
        '-c','../miniCity/miniCity-tf.sumo.cfg','--remote-port','8813'],
        stdout=sys.stdout, stderr=sys.stderr)
    traci.init(8813)

    #traci.start(sumoCmd)

    #trackers
    dfQueueTracker = {}
    dfWaitingTracker = {}
    dfSpeedTracker = {}
    dfActions = pd.DataFrame()
    dfSeconds = pd.DataFrame()
    for i in range(var.num_agentsTF): 
        dfQueueTracker[i] = pd.DataFrame()
        dfWaitingTracker[i] = pd.DataFrame()
        dfSpeedTracker[i] = pd.DataFrame()


    currHod = 0
    currMod = 0
    currSod = 0
    #un dia de simulacion
    while currSod < var.secondsInDay: 
        if currHod != currSod/var.secondsInHour:
            currHod = int(currSod/var.secondsInHour)
            currMod = int(currSod/60)
            #print(f'Day = {day}, Hour = {currHod}, Minute = {currMod}')

        actions = []
        travelTimes = []
        #============== IS TIME TO MAKE A COLLECTIVE DECISION?

        actions = getActions(currSod)
        
        if(currSod%(var.minTimeInYellow + var.minTimeInGreen) == 0): 
            getTrafficData(currSod)    
            #Save sequence of actions taken by vertex agents
            # actions = getActions(currSod)
            #Compute travel times
            travelTimes = getTravelTimes()
            # print(f'Travel time = {travelTimes} min')
        
        data = SumoData()
        data.time_stamp = currSod
        if len(actions) > 0:
            for i in range(len(var.agentsTF)):
                action = data.action.add()
                action.agent_id = i
                action.action = actions[i]        
            data.travel_times.extend(travelTimes)
            #times = travelTimes

        
        # print('Escribiendo datos de tiempos de viaje')
        fifo = open(FIFO, 'rb')
        fifo.read()
        fifo.close()
        fifo = open(FIFO, 'wb')
        fifo.write(data.SerializeToString())
        fifo.close()
        # print('Finalizado')

        currSod += 1
        traci.simulationStep() 
    traci.close() #End on day of simulation