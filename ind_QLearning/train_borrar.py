import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo-gui" #sumo-gui
import random
import pandas as pd
import numpy as np
import math
import var
import gets
import time

dfRewVals = {}
dfQueueTracker = {}
dfWaitingTracker = {} 
dfActions = {}
dfEpsilon = {}
path = '~/Documents/BogotaRL/ind_QLearning/csv_files_train/'

tls = 'tls_14_45'

def debug_phase(tls, currSod):
    ryg_state = traci.trafficlight.getRedYellowGreenState(str(tls))
    p_index = var.agent_TLS[tls].phases.index(ryg_state)
    print('Sec: '+str(currSod) + '   Phase: '+str(ryg_state))

def ind_QLearning():  
    for day in range(0,var.episodes):
        fileOut = open("days.csv","w")
        fileOut.write("Training day: "+str(day)+"\n")
        fileOut.close()
        
        sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
        traci.start(sumoCmd)

        var.agent_TLS[tls].ini4learning()

        for currSod in range(0,var.secondsInDay):
            if(currSod == 0):  
                gets.getObservation()
                var.agent_TLS[tls].getState(currSod)
                traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)
            else:    
                #Sample the system
                if(currSod%var.sampleTime == 0):
                    #Update last state-action                   
                    #Get new state    
                    gets.getObservation()  
                    #Update rewards and update policy
                    var.agent_TLS[tls].updateReward1()
                    var.agent_TLS[tls].updateReward2()  
                    #Q-Learning
                    if var.agent_TLS[tls].finishPhase[1]:
                        print('learning')
                        var.agent_TLS[tls].updateStateAction()
                        var.agent_TLS[tls].learnPolicy(currSod)
                        var.agent_TLS[tls].getAction(day, currSod)                  
                
            # if var.agent_TLS[tls].finishPhase[1]:
            #   action = input('new action')
            #   var.agent_TLS[tls].changeAction(int(action), currSod)
            print(var.agent_TLS[tls].finishPhase)
            var.agent_TLS[tls].setPhase(currSod)
            traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)

            traci.simulationStep()  
            debug_phase('tls_14_45', currSod)
            time.sleep(3)
                
                
        traci.close()