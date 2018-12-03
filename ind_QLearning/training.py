'''
Created on Nov 2018

@author: carolina

Independent Q learning
'''

import os, sys
import subprocess
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
import time

dfRewVals = {}
dfQueueTracker = {}
dfWaitingTracker = {} 
dfActions = {}
dfEpsilon = {}
path = '~/Documents/BogotaRL/ind_QLearning/csv_files_train/'

def saveData(currSod):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon
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
	#Rewards, actions and epsilon
	auxA = [currSod]
	auxE = [currSod]
	for tls in var.agent_TLS.keys():
		auxR = [currSod]            
		auxR.append(var.agent_TLS[tls].currReward)
		auxR.append(var.agent_TLS[tls].currReward2)
		auxA.append(var.agent_TLS[tls].currAction)
		auxE.append(var.agent_TLS[tls].epsilon)
		df = pd.DataFrame([auxR])
		dfRewVals[tls] = dfRewVals[tls].append(df, ignore_index=True)
	df = pd.DataFrame([auxA])
	dfActions = dfActions.append(df, ignore_index=True)
	df = pd.DataFrame([auxE])
	dfEpsilon = dfEpsilon.append(df, ignore_index=True)

def data2files(day):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon, path
	#Save actions and epsilons in file
	aux = ['sec']
	for tls in var.agent_TLS.keys():
		aux.append(tls)
	dfActions.columns = aux
	dfEpsilon.columns = aux
	dfActions.to_csv(path + 'indQ_actions_day' + str(day) + '.csv')
	dfEpsilon.to_csv(path + 'indQ_epsilon_day' + str(day) + '.csv')
	
	#Save rewards in file
	aux = ['sec', 'rew1', 'rew2']
	for tls in var.agent_TLS.keys():
		dfRewVals[tls].columns = aux
		dfRewVals[tls].to_csv(path + 'indQ_rewards_' + str(tls) + '_day' + str(day) + '.csv')
	
	#Save queues and times for each junction
	for j in var.junctions.keys():
		aux = ['currSod']        
		for edge in var.junctions[j].edges:
			aux.append(edge)
		dfQueueTracker[j].columns = aux
		dfWaitingTracker[j].columns = aux
		dfQueueTracker[j].to_csv(path + 'indQ_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		dfWaitingTracker[j].to_csv(path + 'indQ_times_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		
	#Save learning for each agent
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].saveLearning(day, path)


def debug_phase(tls, currSod):
	ryg_state = traci.trafficlight.getRedYellowGreenState(str(tls))
	p_index = var.agent_TLS[tls].phases.index(ryg_state)
	print('Sec: '+str(currSod) + '   Phase: '+str(ryg_state))


def ind_QLearning():  
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon  
		
	for day in range(0,var.episodes):
		fileOut = open("days.csv","w")
		fileOut.write("Training day: "+str(day)+"\n")
		fileOut.close()
		
		sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
		traci.start(sumoCmd)     
		
		dfRewVals = {}
		dfQueueTracker = {}
		dfWaitingTracker = {} 
		dfActions = pd.DataFrame()
		dfEpsilon = pd.DataFrame()
		
		for j in var.junctions.keys():  
			dfQueueTracker[j] = pd.DataFrame()
			dfWaitingTracker[j] = pd.DataFrame()  
		for tls in var.agent_TLS.keys():
			dfRewVals[tls] = pd.DataFrame()
			var.agent_TLS[tls].ini4learning()
		
		#Begins simulation of 1 day           
		for currSod in range(0,var.secondsInDay):
			if(currSod == 0):  
				gets.getObservation()
				for tls in var.agent_TLS.keys():                    
					var.agent_TLS[tls].getState(currSod)
					traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)
			else:    
				#Sample the system
				if(currSod%var.sampleTime == 0):
					#Get new state    
					gets.getObservation()  
					#Update rewards and update policy             
					for tls in var.agent_TLS.keys():
						var.agent_TLS[tls].updateReward1()
						#var.agent_TLS[tls].updateReward2()  
						#Q-Learning
						if var.agent_TLS[tls].finishPhase[1]:
							var.agent_TLS[tls].updateStateAction()
							var.agent_TLS[tls].learnPolicy(currSod)
							var.agent_TLS[tls].getAction(day, currSod)
					saveData(currSod)  
				
			for tls in var.agent_TLS.keys():
				var.agent_TLS[tls].setPhase(currSod)
				traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)

			traci.simulationStep()
			#debug_phase('tls_14_45', currSod)				
				
		traci.close()
		#End simulation of 1 day
		
		data2files(day)
	#-----------------------------------------------------
	fileOut = open("days.csv","w")
	fileOut.write("End training \n")
	fileOut.close()
