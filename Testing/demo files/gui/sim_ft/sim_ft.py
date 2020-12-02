import os, sys
import subprocess

sys.path.insert(0, '../')
from sumo_data_pb2 import SumoData

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(tools)
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

sumoBinary = "sumo-gui"  # sumo-gui
sumoCmd = [sumoBinary, "-c", "../miniCity/miniCity-tf.sumo.cfg", "--no-step-log", "true"]

import random
import pandas as pd
import numpy as np
import sim_ft.var as var

def getTrafficData(currSod):
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker
    for v in range(var.num_agentsTF):
        # ================= count halted vehicles (4 elements)        f
        for edge in var.agentsTF[v].listEdges:
            var.agentsTF[v].queueTracker[edge] = traci.edge.getLastStepHaltingNumber(str(edge))  # num vehicles
            var.agentsTF[v].waitingTracker[edge] = traci.edge.getWaitingTime(str(edge))  # s
            var.agentsTF[v].speedTracker[edge] = traci.edge.getLastStepMeanSpeed(str(edge))  # m/s
        aux_queue = [currSod]
        aux_waiting = [currSod]
        aux_speed = [currSod]
        for edge in var.agentsTF[v].listEdges:
            aux_queue.append(var.agentsTF[v].queueTracker[edge])
            aux_waiting.append(var.agentsTF[v].waitingTracker[edge])
            aux_speed.append(var.agentsTF[v].speedTracker[edge])
        # queue
        df = pd.DataFrame([aux_queue])
        dfQueueTracker[v] = dfQueueTracker[v].append(df, ignore_index=True)
        if len(dfQueueTracker[v]) > var.WINDOW:
            dfQueueTracker[v] = dfQueueTracker[v].drop(dfQueueTracker[v].index[0])
        # waiting time
        df = pd.DataFrame([aux_waiting])
        dfWaitingTracker[v] = dfWaitingTracker[v].append(df, ignore_index=True)
        if len(dfWaitingTracker[v]) > var.WINDOW:
            dfWaitingTracker[v] = dfWaitingTracker[v].drop(dfWaitingTracker[v].index[0])
        # speed
        df = pd.DataFrame([aux_speed])
        dfSpeedTracker[v] = dfSpeedTracker[v].append(df, ignore_index=True)
        if len(dfSpeedTracker[v]) > var.WINDOW:
            dfSpeedTracker[v] = dfSpeedTracker[v].drop(dfSpeedTracker[v].index[0])


def getActions(currSod):
    global dfActions
    aux = [currSod]
    for v in range(var.num_agentsTF):
        aux.append(int(traci.trafficlights.getPhase(str(v))))
    df = pd.DataFrame([aux])
    dfActions = dfActions.append(df, ignore_index=True)
    return aux[1:len(aux)]


def getTravelTimes():
    travel_times = np.zeros([len(var.routes)])
    for r in range(len(var.routes)):
        for i in range(len(var.routes[r]['route_agents'])):
            agent = var.routes[r]['route_agents'][i]
            edge = var.routes[r]['route_edge'][i] + 1
            num_veh = np.mean(np.array(dfQueueTracker[agent][edge].data))
            waitTime = np.mean(np.array(dfWaitingTracker[agent][edge].data)) / num_veh
            speed = np.mean(np.array(dfSpeedTracker[agent][edge].data))
            length = var.agentsTF[agent].lengthEdges[edge - 1]
            travel_times[r] += (waitTime + length / speed) / 60.0
    return travel_times

dfQueueTracker = {}
dfWaitingTracker = {}
dfSpeedTracker = {}
dfActions = pd.DataFrame()

currHod = 0
currMod = 0
currSod = 0

def sim_start_day():
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dfActions, currHod, currMod, currSod
    traci.start(sumoCmd)

    # trackers
    dfQueueTracker = {}
    dfWaitingTracker = {}
    dfSpeedTracker = {}
    dfActions = pd.DataFrame()
    for i in range(var.num_agentsTF):
        dfQueueTracker[i] = pd.DataFrame()
        dfWaitingTracker[i] = pd.DataFrame()
        dfSpeedTracker[i] = pd.DataFrame()

    currHod = 0
    currMod = 0
    currSod = 0

def sim_stop_day():
    traci.close()

def sim_step_day():
    global dfQueueTracker, dfWaitingTracker, dfSpeedTracker, dfActions, currHod, currMod, currSod

    traci.simulationStep()
    currSod += 1

    if currHod != currSod / var.secondsInHour:
        currHod = int(currSod / var.secondsInHour)
        currMod = int(currSod / 60)
        # print(f'Day = {day}, Hour = {currHod}, Minute = {currMod}')

    actions = []
    travelTimes = []
    # ============== IS TIME TO MAKE A COLLECTIVE DECISION?
    if (currSod % (var.minTimeInYellow + var.minTimeInGreen) == 0):
        getTrafficData(currSod)
        # Save sequence of actions taken by vertex agents
        actions = getActions(currSod)
        # Compute travel times
        travelTimes = getTravelTimes()
        print(f'Travel time = {travelTimes} min')

    data = SumoData()
    data.time_stamp = currSod
    if len(actions) > 0:
        for i in range(len(var.agentsTF)):
            action = data.action.add()
            action.agent_id = i
            action.action = actions[i]
        data.travel_times.extend(travelTimes)
        # times = travelTimes

    return data