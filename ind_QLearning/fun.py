'''
Created on Nov 2018

@author: carolina
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
import sklearn
from sklearn.cluster import KMeans
import var
import gets

exec(open("./var.py").read())
exec(open("./gets.py").read())
observations = {}

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
					stateDataEntry = []
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
	for tls in var.agent_TLS:
		x = int(sum(np.std(observations[tls], axis=0)))
		print(tls + ' - ' + str(x))
	
	# for tls in var.agent_TLS:
	#     fileOut = open("./csv_files_obs/recoveryStates_tls"+str(tls)+".csv","w")
	#     var.agent_TLS[tls].numClustersTracker = int(sum(np.std(observations[tls], axis=0)))
	#     if( var.agent_TLS[tls].numClustersTracker < var.min_numStates):
	#         var.agent_TLS[tls].numClustersTracker = var.min_numStates        
	#     var.agent_TLS[tls].numStates = var.agent_TLS[tls].numClustersTracker
	#     var.agent_TLS[tls].mapDiscreteStates = range(0,var.agent_TLS[tls].numStates)
	#     var.agent_TLS[tls].dictClusterObjects = KMeans(n_clusters=var.agent_TLS[tls].numClustersTracker)
	#     var.agent_TLS[tls].dictClusterObjects.fit(observations[tls])
	#     coord = var.agent_TLS[tls].dictClusterObjects.cluster_centers_
	#     for k in range(0,var.agent_TLS[tls].numClustersTracker):            
	#         map(lambda y: fileOut.write("  " + str(y)), coord[k])
	#         fileOut.write("\n")
	#     fileOut.close()
	#     print ("tls: " + str(tls) + " - clusters: " + str(var.agent_TLS[tls].numStates))

def writeDataClusters():
	dfClusters = pd.DataFrame()
	for tls in var.agent_TLS:
		df = pd.DataFrame([[tls,  var.agent_TLS[tls].numClustersTracker]])
		dfClusters = dfClusters.append(df, ignore_index=True) 
	aux = ['tls', 'states']
	dfClusters.columns = aux
	dfClusters.to_csv('./csv_files_obs/dfClusters.csv')
		
		
	
	
							
						
				
		
	
	

