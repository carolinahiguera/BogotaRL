'''
Created on oct, 2018

@author: carolina
FIXED TIME CONTROL FOR TRAFFIC LIGHTS - BOGOTA SCENARIO
'''

import os, sys


if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
sumoBinary = "sumo" #sumo-gui

import random
import pandas as pd
import numpy as np
import math
import var
import gets

execfile("./var.py")
execfile("./gets.py")


dfRewVals = {}
dfQueueTracker = {}
dfWaitingTracker = {} 

def saveData(currSod):
	global dfQueueTracker, dfWaitingTracker, dfRewVals
	#Queues and waiting times
	for j in var.junctions.keys():
		auxQ = [currSod]
		auxW = [currSod]
		for edge in range(0,len(var.junctions[j].edges)):
			junction = var.agent_TLS[var.junctions[j].tls].listJunctions.index(j)
			queue = var.agent_TLS[var.junctions[j].tls].queueEdgeTracker[junction][edge]
			waitTime = var.agent_TLS[var.junctions[j].tls].waitingEdgeTracker[junction][edge]
			auxQ.append(queue)
			auxW.append(waitTime)
		df = pd.DataFrame([auxQ])
		dfQueueTracker[j] = dfQueueTracker[j].append(df, ignore_index=True) 
		df = pd.DataFrame([auxW])
		dfWaitingTracker[j] = dfWaitingTracker[j].append(df, ignore_index=True)
	#Rewards    
	for tls in var.agent_TLS.keys():
		auxR = [currSod]            
		auxR.append(var.agent_TLS[tls].currReward)
		auxR.append(var.agent_TLS[tls].currReward2)        
		df = pd.DataFrame([auxR])
		dfRewVals[tls] = dfRewVals[tls].append(df, ignore_index=True)
	
	
		
def data2files(day):
	global dfQueueTracker, dfWaitingTracker, dfRewVals
		
	#Save rewards in file
	aux = ['sec', 'rew1', 'rew2']
	for tls in var.agent_TLS.keys():
		dfRewVals[tls].columns = aux
		dfRewVals[tls].to_csv('./csv_files/ft_rewards_' + str(tls) + '_day' + str(day) + '.csv')
	
	#Save queues and times for each junction
	for j in var.junctions.keys():
		aux = ['currSod']        
		for edge in var.junctions[j].edges:
			aux.append(edge)
		dfQueueTracker[j].columns = aux
		dfWaitingTracker[j].columns = aux
		dfQueueTracker[j].to_csv('./csv_files/ft_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		dfWaitingTracker[j].to_csv('./csv_files/ft_times_' + var.junctions[j].name + '_day' + str(day) + '.csv')

#Inicio episodios
for day in range(0,var.episodes):
	print("Day: " + str(day) + "\n")
	fileOut = open("days.csv","w")
	fileOut.write("TF day: "+str(day)+"\n")
	fileOut.close()    

	sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
	traci.start(sumoCmd) 

	dfRewVals = {}
	dfQueueTracker = {}
	dfWaitingTracker = {} 

	for j in var.junctions.keys():  
		dfQueueTracker[j] = pd.DataFrame()
		dfWaitingTracker[j] = pd.DataFrame()  
	for tls in var.agent_TLS.keys():
		dfRewVals[tls] = pd.DataFrame()
	
	#Begins simulation of 1 day           
	for currSod in range(0,var.secondsInDay):
		traci.simulationStep()               	
		gets.getObservation()
		gets.getCurrentAction()
		for tls in var.agent_TLS.keys():
			var.agent_TLS[tls].updateReward1()
			var.agent_TLS[tls].updateReward2()
		saveData(currSod)    
	traci.close()
	#End simulation of 1 day
	
	data2files(day)
#-----------------------------------------------------
fileOut = open("days.csv","w")
fileOut.write("End simulation \n")
fileOut.close()


# step = 0
# while step < 1000:
#    traci.simulationStep()
#    x = traci.edge.getLastStepVehicleNumber("gneE46")
#    print("Last step " + str(x) + " vehicles\n")   
#    step += 1
# traci.close(False)