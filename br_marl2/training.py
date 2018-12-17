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
path = var.trainPath

def saveData(currSod):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon
	row = round(currSod/var.sampleTime)
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
		dfQueueTracker[j].loc[row] = np.array([auxQ])
		dfWaitingTracker[j].loc[row] = np.array([auxW])		
	#Rewards, actions and epsilon
	auxA = [currSod]
	auxE = [currSod]
	for tls in var.agent_TLS.keys():
		auxR = [currSod]            
		auxR.append(var.agent_TLS[tls].currReward)		
		auxA.append(var.agent_TLS[tls].currAction)
		auxE.append(var.agent_TLS[tls].epsilon)
		df = pd.DataFrame([auxR])
		dfRewVals[tls].loc[row] = np.array([auxR])
	dfActions.loc[row] = np.array([auxA]) 
	dfEpsilon.loc[row] = np.array([auxE])

def data2files(day):
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon, path
	#Save actions and epsilons in file
	aux = ['sec']
	for tls in var.agent_TLS.keys():
		aux.append(tls)
	dfActions.columns = aux
	dfEpsilon.columns = aux
	dfActions.to_csv(path + 'br_actions_day' + str(day) + '.csv')
	dfEpsilon.to_csv(path + 'br_epsilon_day' + str(day) + '.csv')
	
	#Save rewards in file
	aux = ['sec', 'rew1']
	for tls in var.agent_TLS.keys():
		dfRewVals[tls].columns = aux
		dfRewVals[tls].to_csv(path + 'br_rewards_' + str(tls) + '_day' + str(day) + '.csv')
	
	#Save queues and times for each junction
	for j in var.junctions.keys():
		aux = ['currSod']        
		for edge in var.junctions[j].edges:
			aux.append(edge)
		dfQueueTracker[j].columns = aux
		dfWaitingTracker[j].columns = aux
		dfQueueTracker[j].to_csv(path + 'br_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		dfWaitingTracker[j].to_csv(path + 'br_times_' + var.junctions[j].name + '_day' + str(day) + '.csv')
		
	#Save learning for each agent
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].saveLearning(day, path)


def debug_phase(tls, currSod):
	ryg_state = traci.trafficlight.getRedYellowGreenState(str(tls))
	p_index = var.agent_TLS[tls].phases.index(ryg_state)
	print('Sec: '+str(currSod) + '   Phase: '+str(ryg_state))


def ini_dataframes():
	global dfQueueTracker, dfWaitingTracker, dfRewVals, dfActions, dfEpsilon  
	dfRewVals = {}
	dfQueueTracker = {}
	dfWaitingTracker = {} 
	rows = int(round(var.secondsInDay/var.sampleTime))
	for j in var.junctions.keys():
		cols = len(var.junctions[j].edges) + 1
		dfQueueTracker[j] = pd.DataFrame(index=range(rows), columns=range(cols))
		dfWaitingTracker[j] = pd.DataFrame(index=range(rows), columns=range(cols))
	for tls in var.agent_TLS.keys():
		dfRewVals[tls] = pd.DataFrame(index=range(rows), columns=range(2))
	dfActions = pd.DataFrame(index=range(rows), columns=range(1+len(var.agent_TLS)))
	dfEpsilon = pd.DataFrame(index=range(rows), columns=range(1+len(var.agent_TLS)))

def br_marl_learning():
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].initialize()
	#learn previously from Fixed Time control to speed up learning
	for day in range(0,int(var.episodes*var.pTransfer)):
		fileOut = open("days.csv","w")
		fileOut.write("Training day with FT: "+str(day)+"\n")
		fileOut.close()
		
		sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
		traci.start(sumoCmd)     
		
		ini_dataframes()		

		for currSod in range(0,var.secondsInDay):
			traci.simulationStep()
			gets.getObservation(currSod)
			#FT control
			for tls in var.agent_TLS.keys():
				var.agent_TLS[tls].ft_check_complete_phase(currSod)
				if var.agent_TLS[tls].finishPhase[1]:
					var.agent_TLS[tls].ft_get_phase(currSod)
					traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)
			if currSod>120:
				for tls in var.agent_TLS.keys():
					var.agent_TLS[tls].getJointAction()
				#update Q(s,a) values
				for tls in var.agent_TLS.keys():
					if var.agent_TLS[tls].change_action:
						if (currSod%var.sampleTime)==0 and currSod<=var.agent_TLS[tls].finishPhase[0]:
							# print('updating q '+tls)
							gets.getObservationNow()
							var.agent_TLS[tls].receive_reward()
							var.agent_TLS[tls].updateQValue(currSod)	
			if (currSod%var.sampleTime == 0):
				saveData(currSod)
		data2files(day)
		traci.close()

	#switch to br-marl 
	for day in range(int(var.episodes*var.pTransfer), var.episodes):
		fileOut = open("days.csv","w")
		fileOut.write("Training day with BR: "+str(day)+"\n")
		fileOut.close()
		
		sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
		traci.start(sumoCmd)     
		
		ini_dataframes()
		for tls in var.agent_TLS.keys():
			var.agent_TLS[tls].set_first_action()
		#print('Day: ' + str(day))

		for currSod in range(0,var.secondsInDay):
			#print('currSod: ' + str(currSod))
			traci.simulationStep()
			gets.getObservation(currSod)
			for tls in var.agent_TLS.keys():
				#print('TLS: '+tls)
				if var.agent_TLS[tls].finishPhase[1]:
					#sprint('br_marl')
					var.agent_TLS[tls].receive_reward()
					var.agent_TLS[tls].updateStateAction()
					var.agent_TLS[tls].learnPolicy(currSod, day)
					var.agent_TLS[tls].getAction(day, currSod)
			for tls in var.agent_TLS.keys():
				var.agent_TLS[tls].getJointAction()
			for tls in var.agent_TLS.keys():
				var.agent_TLS[tls].setPhase(currSod)
				traci.trafficlight.setRedYellowGreenState(tls, var.agent_TLS[tls].RedYellowGreenState)

			if (currSod%var.sampleTime == 0):
				saveData(currSod)
		data2files(day)
		traci.close()
	#-----------------------------------------------------
	fileOut = open("days.csv","w")
	fileOut.write("End training \n")
	fileOut.close()


