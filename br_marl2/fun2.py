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
path = '~/Documents/BogotaRL/br_marl/csv_files_obs/'

def learnDiscretization():
	global observations
	observations = {}
	for tls in var.agent_TLS.keys():
		var.agent_TLS[tls].initialize()
		observations[tls] = {}
		for nb in var.agent_TLS[tls].neighbors:
			observations[tls][nb] = np.array([])
	
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
					for nb in var.agent_TLS[tls].neighbors:
						stateDataEntry = gets.getObservation_NB(tls, nb, currSod)
						if(len(observations[tls][nb]) == 0):
							observations[tls][nb] = np.array([stateDataEntry])
						else:
							observations[tls][nb] = np.vstack([observations[tls][nb], stateDataEntry])

		traci.close()
		#End simulation of 1 day	

	fileOut = open("days.csv","w")
	fileOut.write("End of observation")
	fileOut.close()
	#End of observation days
	#Number of centroids for each tls
	for tls in var.agent_TLS.keys():
		for nb in var.agent_TLS[tls].neighbors:
			x = int(sum(np.std(observations[tls][nb], axis=0)))
			print(tls + ' - ' + nb + '---->' + str(x))
	#Vector quatization
	for tls in var.agent_TLS.keys():
		for nb in var.agent_TLS[tls].neighbors:
			var.agent_TLS[tls].normalize[nb] = np.array(np.std(observations[tls][nb],axis=0))
			whitened = whiten(observations[tls][nb])
			codes = round(sum(var.agent_TLS[tls].normalize[nb]))
			if codes < var.min_numStates:
				codes = var.min_numStates
			var.agent_TLS[tls].numJointStates[nb] = codes
			var.agent_TLS[tls].codebook[nb] = kmeans(whitened,codes)[0]
			df = pd.DataFrame(var.agent_TLS[tls].codebook[nb])
			df.to_csv(path+'codebook_'+tls+'_'+nb+'.csv')
			df = pd.DataFrame(var.agent_TLS[tls].normalize[nb])
			df.to_csv(path+'normalize_'+tls+'_'+nb+'.csv')
		
