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
path = '~/Documents/BogotaRL/ve_marl/csv_files_obs/'

def learnDiscretization():
	global observations
	observations = {}
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].initialize()
	rows = var.secondsInDay*var.days2Observe
	for edge in var.agent_Edge.keys():
		cols = 1
		for j in var.agent_TLS[edge[0]].listJunctions:
			cols += len(var.junctions[j].edges)*2
		for j in var.agent_TLS[edge[1]].listJunctions:
			cols += len(var.junctions[j].edges)*2
		observations[edge] = np.zeros((rows,cols))
		
	
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
				for edge in var.agent_Edge.keys():
					stateDataEntry = gets.getObservation_NB(edge[0], edge[1], currSod)
					observations[edge][currSod+(day*var.secondsInDay),] = stateDataEntry

		traci.close()
		#End simulation of 1 day	

	fileOut = open("days.csv","w")
	fileOut.write("End of observation")
	fileOut.close()
	#End of observation days
	#Number of centroids for each tls
	for edge in var.agent_Edge.keys():		
		x = int(sum(np.std(observations[edge], axis=0)))
		print(edge[0] + ' - ' + edge[1] + '---->' + str(x))
	#Vector quatization
	for edge in var.agent_Edge.keys():		
		var.agent_Edge[edge].normalize = np.array(np.std(observations[edge],axis=0))
		whitened = whiten(observations[edge])
		codes = round(sum(var.agent_Edge[edge].normalize))
		if codes < var.min_numStates:
			codes = var.min_numStates
		var.agent_Edge[edge].numJointStates = codes
		var.agent_Edge[edge].codebook = kmeans(whitened,codes)[0]
		df = pd.DataFrame(var.agent_Edge[edge].codebook)
		df.to_csv(path+'codebook_'+edge[0]+'_'+edge[1]+'.csv')
		df = pd.DataFrame(var.agent_Edge[edge].normalize)
		df.to_csv(path+'normalize_'+edge[0]+'_'+edge[1]+'.csv')
		
