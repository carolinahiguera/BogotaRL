import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo" #sumo-gui
from scipy.cluster.vq import vq, kmeans, whiten
import numpy as np
import pandas as pd
import var
import gets


exec(open("./var.py").read())
exec(open("./gets.py").read())
observations = {}
path = '~/Documents/BogotaRL/ind_QLearning/csv_files_obs/'

def learnDiscretization():
	global observations
	observations = {}
	for tls in var.agent_TLS:
		var.agent_TLS[tls].initialize()
		observations[tls] = np.array([])
	
	for day in range(0,var.days2Observe):
		print("Observation day: " + str(day))
		fileOut = open("days.csv","w")
		fileOut.write("Observation day: "+str(day)+"\n")
		fileOut.close()		
		sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
		traci.start(sumoCmd)		
		#Begins simulation of 1 day           
		for currSod in range(0,var.secondsInDay):
			traci.simulationStep()     
			#Sample state observation
			if(currSod%var.sampleTime == 0):
				gets.getObservation()                
				for tls in var.agent_TLS.keys():
					stateDataEntry = [int(currSod/3600)+6]
					for j in range(0,len(var.agent_TLS[tls].listJunctions)):
						jID = var.agent_TLS[tls].listJunctions[j]
						for e in range(0,len(var.junctions[jID].edges)):
							stateDataEntry.append(var.agent_TLS[tls].queueEdgeTracker[j][e])
					for j in range(0,len(var.agent_TLS[tls].listJunctions)):
						jID = var.agent_TLS[tls].listJunctions[j]
						for e in range(0,len(var.junctions[jID].edges)):
							stateDataEntry.append(var.agent_TLS[tls].waitingEdgeTracker[j][e])
					if len(observations[tls]) == 0:
						observations[tls] = np.array([stateDataEntry])
					else:
						observations[tls] = np.vstack([observations[tls], stateDataEntry])        
		traci.close()
		#End simulation of 1 day		
	fileOut = open("days.csv","w")
	fileOut.write("End of observation")
	fileOut.close()
	#End of observation days
	#Number of centroids for each tls
	for tls in var.agent_TLS.keys():
		x = int(sum(np.std(observations[tls], axis=0)))
		print(tls + ' - ' + str(x))
	#Vector quatization
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].normalize = np.array(np.std(observations[tls],axis=0))
		whitened = whiten(observations[tls])
		codes = round(sum(var.agent_TLS[tls].normalize))
		if codes < var.min_numStates:
			codes = var.min_numStates
		var.agent_TLS[tls].numStates = codes
		var.agent_TLS[tls].codebook = kmeans(whitened,codes)[0]
		df = pd.DataFrame(var.agent_TLS[tls].codebook)
		df.to_csv(path+'codebook_'+tls+'.csv')
		df = pd.DataFrame(var.agent_TLS[tls].normalize)
		df.to_csv(path+'normalize_'+tls+'.csv')
		
