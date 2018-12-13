'''
Created on Nov 27, 2017

@author: carolina
'''
import var
import numpy as np
import pandas as pd
import random
import itertools
from scipy.cluster.vq import vq, kmeans, whiten
path_obs = '~/Documents/BogotaRL/br_marl/csv_files_obs/'


class TLS(object):

	def __init__(self, ID, listJunctions, phases, actionPhases, auxPhases, beta, 
		neighbors, plan2, plan3, plan4):
		self.ID = ID
		self.listJunctions = listJunctions
		self.phases = phases
		self.actionPhases = actionPhases
		self.auxPhases = auxPhases
		self.beta = beta
		self.neighbors = neighbors
		self.plan2 = plan2
		self.plan3 = plan3
		self.plan4 = plan4
		self.finishPhase = [-1, True]
		self.counterPlan = 0
		self.RedYellowGreenState = ''
		self.change_action = False

		#Almacena informacion del agente por interseccion (colas, tiempo de espera)  
		self.queueEdgeTracker = {}
		self.waitingEdgeTracker = {}
		self.speedEdgeTracker = {}
		self.queueLaneTracker = {}
		self.waitingLaneTracker = {}  
		self.speedLaneTracker = {} 

		#Parametros del aprendizaje
		self.currAction = -1
		self.lastAction = -1
		self.currReward  = 0
		self.currJointAction = {}
		self.currJointState = {}
		self.lastJointAction = {}
		self.lastJointState = {}
		self.QValues = {}
		self.M = {}
		self.V = {}		
		#Discretizacion de espacio de estados       
		self.numActions = len(self.actionPhases)
		self.numJointStates = {}
		self.numJointActions = {}
		self.jointActions = {}
		self.codebook = {}
		self.normalize = {}
		for nb in self.neighbors:
			self.codebook[nb] = None
			self.normalize[nb] = None
			self.numJointStates[nb] = None
			self.jointActions[nb] = None
			self.numJointActions[nb] = None
			self.QValues[nb] = None			
			self.M[nb] = None
			self.V[nb] = None
			self.currJointAction[nb] = None
			self.currJointState[nb] = None
			self.lastJointAction[nb] = None
			self.lastJointState[nb] = None

	def initialize(self):
		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			self.queueEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			self.waitingEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges)) #EN MINUTOS
			self.speedEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			self.queueLaneTracker[j] = {}
			self.waitingLaneTracker[j] = {} 
			self.speedLaneTracker[j] = {}  
			for e in range(0,len(var.junctions[jName].edges)):
				self.queueLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
				self.waitingLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN MINUTOS
				self.speedLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))				

		for nb in self.neighbors:
			aux = []
			df = pd.read_csv(path_obs+'codebook_'+self.ID+'_'+nb+'.csv')
			data = df.values
			self.numJointStates[nb] = len(data)
			for i in range(0,len(data)):
				aux.append(np.delete(data[i],0))
			self.codebook[nb] = np.array(aux)
			aux = []
			df = pd.read_csv(path_obs+'normalize_'+self.ID+'_'+nb+'.csv')
			data = df.values
			for i in range(0,len(data)):
				aux.append(data[i][1])
			self.normalize[nb] = np.array(aux)

			self.jointActions[nb] = list(itertools.product(self.actionPhases, var.agent_TLS[nb].actionPhases))
			self.numJointActions[nb] = len(self.jointActions[nb])
			self.QValues[nb] = np.zeros((self.numJointStates[nb],self.numJointActions[nb]))			
			nbAct = len(var.agent_TLS[nb].actionPhases)
			self.V[nb] = np.zeros((self.numJointStates[nb],nbAct))
			self.M[nb] = np.ones((self.numJointStates[nb],nbAct))/nbAct

	def ft_get_phase(self,currSod):
		if currSod < 18000:
			#execute plan 2
			action = self.plan2[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan2)
			if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
				self.change_action = True
				self.lastAction = self.currAction
				self.currAction = self.phases.index(self.RedYellowGreenState)
		elif currSod>=18000 and currSod<32400:
			#execute plan 3
			if currSod == 18000:
				self.counterPlan = 0
			action = self.plan3[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan3)
			if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
				self.change_action = True
				self.lastAction = self.currAction
				self.currAction = self.phases.index(self.RedYellowGreenState)
		else:
			#execute plan 4
			if currSod == 32400:
				self.counterPlan = 0
			action = self.plan4[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan4)
			if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
				self.change_action = True
				self.lastAction = self.currAction
				self.currAction = self.phases.index(self.RedYellowGreenState)

	def ft_check_complete_phase(self, currSod):
		if currSod == self.finishPhase[0]:
			self.finishPhase = [-1, True]

	#Q LEARNING FUNTIONS-------------------------------------------------

	def receive_reward(self):
		reward = 0.0
		acc = 0.0
		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			for e in range(0,len(var.junctions[jName].edges)):
				acc += 1.0
				a = self.beta[0]*41.0/(self.queueEdgeTracker[j][e]+1.0)
				b = self.beta[1]*201.0/(self.waitingEdgeTracker[j][e]+1.0)
				reward += (a + b)
		rmax = 	(self.beta[0]*41.0+ self.beta[1]*201.0)*acc
		self.currReward = 2.0*(reward/rmax) - 1.0

	#def updateQValue(self):

		
		