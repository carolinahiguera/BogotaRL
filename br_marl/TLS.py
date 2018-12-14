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
path = '~/Documents/BogotaRL/br_marl/csv_files_obs/'
path2 = '~/Documents/BogotaRL/br_marl/csv_files_train/'

class TLS(object):
	'''
	classdocs
	'''


	def __init__(self, ID, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp, neighbors):
		self.ID = ID
		self.listJunctions = listJunctions
		self.phases = phases
		self.actionPhases = actionPhases
		self.auxPhases = auxPhases
		self.neighbors = neighbors
		
		#Almacena informacion del agente por interseccion (colas, tiempo de espera)  
		self.queueEdgeTracker = {}
		self.waitingEdgeTracker = {}
		self.speedEdgeTracker = {}
		self.queueLaneTracker = {}
		self.waitingLaneTracker = {}  
		self.speedLaneTracker = {} 
		
		#Estado y recompensa     
		self.currReward = 0
		self.currReward2 = 0
		self.currAction = -1
		self.lastAction = -1
		self.currJointAction = {}
		self.currJointState = {}
		self.lastJointAction = {}
		self.lastJointState = {}
		self.RedYellowGreenState = ''
		self.beta = beta
		self.theta = theta        
		self.exp = exp
		self.gamma = 0.9
		self.epsilon = 1.0
		self.setInYellow = -1
		self.finishPhase = [-1, True]
		self.timeInGreen = 0
		
		
		#Q matrix
		self.QValues = {}
		self.QCounts = {}
		self.QAlpha ={}
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
			self.QCounts[nb] = None
			self.QAlpha[nb] =None
			self.M[nb] = None
			self.V[nb] = None
			self.currJointAction[nb] = None
			self.currJointState[nb] = None
			self.lastJointAction[nb] = None
			self.lastJointState[nb] = None
		
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
				self.speedLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN M/S
	
	def initialize(self):
		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			self.queueEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			self.waitingEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges)) #EN MINUTOS
			self.speedEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			for e in range(0,len(var.junctions[jName].edges)):
				self.queueLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
				self.waitingLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN MINUTOS
				self.speedLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))				
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishPhase = [-1, True]

	def ini4learning(self):
		for nb in self.neighbors:
			aux = []
			df = pd.read_csv(path+'codebook_'+self.ID+'_'+nb+'.csv')
			data = df.values
			self.numJointStates[nb] = len(data)
			for i in range(0,len(data)):
				aux.append(np.delete(data[i],0))
			self.codebook[nb] = np.array(aux)
			aux = []
			df = pd.read_csv(path+'normalize_'+self.ID+'_'+nb+'.csv')
			data = df.values
			for i in range(0,len(data)):
				aux.append(data[i][1])
			self.normalize[nb] = np.array(aux)

			self.jointActions[nb] = list(itertools.product(self.actionPhases, var.agent_TLS[nb].actionPhases))
			self.numJointActions[nb] = len(self.jointActions[nb])

			self.QValues[nb] = np.zeros((self.numJointStates[nb],self.numJointActions[nb]))
			self.QCounts[nb] = np.zeros((self.numJointStates[nb],self.numJointActions[nb]))
			self.QAlpha[nb] = np.ones((self.numJointStates[nb],self.numJointActions[nb]))
			nbAct = len(var.agent_TLS[nb].actionPhases)
			self.V[nb] = np.zeros((self.numJointStates[nb],nbAct))
			self.M[nb] = np.ones((self.numJointStates[nb],nbAct))/nbAct


		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			self.queueEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			self.waitingEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges)) #EN MINUTOS
			self.speedEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			for e in range(0,len(var.junctions[jName].edges)):
				self.queueLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
				self.waitingLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN MINUTOS
				self.speedLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
	
	def set_first_action(self):	
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.lastAction = self.currAction
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishPhase = [0, False]

	def ini4testing(self):
		for nb in self.neighbors:
			aux = []
			df = pd.read_csv(path+'codebook_'+self.ID+'_'+nb+'.csv')
			data = df.values
			self.numJointStates[nb] = len(data)
			for i in range(0,len(data)):
				aux.append(np.delete(data[i],0))
			self.codebook[nb] = np.array(aux)
			aux = []
			df = pd.read_csv(path+'normalize_'+self.ID+'_'+nb+'.csv')
			data = df.values
			for i in range(0,len(data)):
				aux.append(data[i][1])
			self.normalize[nb] = np.array(aux)

			self.jointActions[nb] = list(itertools.product(self.actionPhases, var.agent_TLS[nb].actionPhases))
			self.numJointActions[nb] = len(self.jointActions[nb])

			df = pd.read_csv(path2+'QValues_' + str(self.ID) +'_' + nb + '_day' + str(var.episodes-1) +'.csv')
			self.QValues[nb] = df.values
			df = pd.read_csv(path2+'QCounts_' + str(self.ID) +'_' + nb + '_day' + str(var.episodes-1) +'.csv')
			self.QCounts[nb] = df.values
			df = pd.read_csv(path2+'QAlphas_' + str(self.ID) +'_' + nb + '_day' + str(var.episodes-1) +'.csv')
			self.QAlpha[nb] = df.values
			df = pd.read_csv(path2+'V_' + str(self.ID) +'_' + nb + '_day' + str(var.episodes-1) +'.csv')
			self.V[nb] = df.values
			df = pd.read_csv(path2+'M_' + str(self.ID) +'_' + nb + '_day' + str(var.episodes-1) +'.csv')
			self.M[nb] = df.values


		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			self.queueEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			self.waitingEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges)) #EN MINUTOS
			self.speedEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
			for e in range(0,len(var.junctions[jName].edges)):
				self.queueLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
				self.waitingLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN MINUTOS
				self.speedLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
		
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.lastAction = self.currAction
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishPhase = [0, False]
	
	def updateStateAction(self):
		self.lastAction = self.currAction
		for nb in self.neighbors:
			self.lastJointAction[nb] = self.currJointAction[nb]
			self.lastJointState[nb] = self.currJointState[nb]        
	
	def updateReward1(self):
		reward = 0
		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			for e in range(0,len(var.junctions[jName].edges)):
				a = (self.beta[0]*self.queueEdgeTracker[j][e])**self.theta[0]
				b = (self.beta[1]*self.waitingEdgeTracker[j][e])**self.theta[1]
				reward -= (a + b)
		self.currReward = reward
	
	def updateReward2(self):
		reward = 0
		for j in range(0,len(self.listJunctions)):
			jName = self.listJunctions[j]
			for e in range(0,len(var.junctions[jName].edges)):
				a = (self.queueEdgeTracker[j][e])**self.exp[1]
				b = (self.waitingEdgeTracker[j][e])**self.exp[0]
				reward -= a*b
		self.currReward2 = reward
	

	def getObservation_NB(self, nb, currSod):
	    #estado del agente tls
	    stateDataEntry = [int(currSod/3600)+6]
	    for j in range(0,len(var.agent_TLS[self.ID].listJunctions)):
	        jID = var.agent_TLS[self.ID].listJunctions[j]
	        for e in range(0,len(var.junctions[jID].edges)):
	            stateDataEntry.append(var.agent_TLS[self.ID].queueEdgeTracker[j][e])
	    for j in range(0,len(var.agent_TLS[self.ID].listJunctions)):
	        jID = var.agent_TLS[self.ID].listJunctions[j]
	        for e in range(0,len(var.junctions[jID].edges)):
	            stateDataEntry.append(var.agent_TLS[self.ID].waitingEdgeTracker[j][e])
	   #estado de su vecino
	    if(nb != -1):
	        for j in range(0,len(var.agent_TLS[nb].listJunctions)):
	            jID = var.agent_TLS[nb].listJunctions[j]
	            for e in range(0,len(var.junctions[jID].edges)):
	                stateDataEntry.append(var.agent_TLS[nb].queueEdgeTracker[j][e])
	        for j in range(0,len(var.agent_TLS[nb].listJunctions)):
	            jID = var.agent_TLS[nb].listJunctions[j]
	            for e in range(0,len(var.junctions[jID].edges)):
	                stateDataEntry.append(var.agent_TLS[nb].waitingEdgeTracker[j][e])
	    return stateDataEntry

	def getJointState(self,currSod):
		for nb in self.neighbors:
			state = self.getObservation_NB(nb, currSod)
			state = np.array([state/self.normalize[nb]]) #verificar
			self.currJointState[nb] = vq(state, self.codebook[nb])[0][0]

	def getJointAction(self):
		act_i = self.currAction
		for nb in self.neighbors:
			act_j = var.agent_TLS[nb].currAction
			jAct = (act_i, act_j)
			self.currJointAction[nb] = self.jointActions[nb].index(jAct)	

	def getBR(self, nb, s):
		QM = np.zeros([len(self.actionPhases)])
		for act_i in self.actionPhases:
			for act_j in var.agent_TLS[nb].actionPhases:
				aij = self.jointActions[nb].index((act_i, act_j))
				QM[act_i] += self.QValues[nb][s,aij] * self.M[nb][s,act_j]
		br = np.max(QM)
		return br

	
	def learnPolicy(self, currSod):
		self.getJointState(currSod)
		for nb in self.neighbors:
			s = self.lastJointState[nb]
			a = self.lastJointAction[nb]
			s_ = self.currJointState[nb]
			r = self.currReward

			act_j = self.jointActions[nb][a][1]
			self.V[nb][s, act_j] += 1.0
			self.M[nb][s, ] = self.V[nb][s, ] / np.sum(self.V[nb][s,])

			br = self.getBR(nb, s_)
			alpha = self.QAlpha[nb][s,a]
			lastQ = self.QValues[nb][s,a]
			self.QValues[nb][s,a] = lastQ + alpha*(r + self.gamma*br - lastQ)
			self.QCounts[nb][s,a] += 1.0
			self.QAlpha[nb][s,a] = 1.0/self.QCounts[nb][s,a]
	
	def getAction(self, day, sec):
		min = int(round(sec/60.0))
		seed = (1.0*day)+(sec/60.0)
		random.seed(seed)
		unigen = random.random()        
		#self.epsilon = np.exp(-(1.0/180.0)*((1.0*day)+(min/60.0))) 
		self.epsilon = np.exp(-(1.0/130.0)*((1.0*day)+(min/60.0))) 
		
		if(unigen < self.epsilon):
			#Explorar
			self.currAction = random.randint(0,len(self.actionPhases)-1) 
		else:
			QM = np.zeros([len(self.actionPhases)])
			for act_i in self.actionPhases:
				for nb in self.neighbors:
					s = self.currJointState[nb]
					for act_j in var.agent_TLS[nb].actionPhases:
						aij = self.jointActions[nb].index((act_i, act_j))
						QM[act_i] += self.QValues[nb][s,aij] * self.M[nb][s,act_j]
			self.currAction = np.argmax(QM)
		self.finishPhase = [sec, False]
		if self.lastAction == self.currAction:
			self.timeInGreen += var.minTimeGreen
		else: 
			self.timeInGreen = 0
		if self.timeInGreen > var.maxTimeGreen:
			self.currAction = 1 if (self.currAction==0) else 0

	def changeAction(self, sec, action):
		self.currAction = action
		self.finishPhase = [sec, False]

	def setPhase(self, currSod):
		aux_phase = self.auxPhases[self.lastAction][self.currAction]
		if(not(type(aux_phase)==list)):
			if aux_phase != -1:
				if currSod <= self.finishPhase[0]+var.timeYellow:
					self.RedYellowGreenState = self.phases[aux_phase]
				elif (currSod > self.finishPhase[0]+var.timeYellow) and (currSod <= self.finishPhase[0]+var.timeYellow+var.minTimeGreen):
					self.RedYellowGreenState = self.phases[self.currAction]
				else:
					self.finishPhase = [-1, True]
			else:
				self.RedYellowGreenState = self.phases[self.currAction]
				if currSod > (self.finishPhase[0]+var.minTimeGreen):
					self.finishPhase = [-1, True]
		else:
			#print(self.ID + '  ' + str(aux_phase))
			if currSod <= self.finishPhase[0]+var.timeYellow:
				self.RedYellowGreenState = self.phases[aux_phase[0]]
			#   print('aca1' + '  ' + self.RedYellowGreenState)
			elif (currSod > self.finishPhase[0]+var.timeYellow) and (currSod <= self.finishPhase[0]+(2*var.timeYellow)):
				self.RedYellowGreenState = self.phases[aux_phase[1]]
			#   print('aca2' + '  ' + self.RedYellowGreenState)
			elif (currSod > self.finishPhase[0]+(2*var.timeYellow)) and (currSod <= self.finishPhase[0]+(3*var.timeYellow)):
				self.RedYellowGreenState = self.phases[aux_phase[2]]
			#   print('aca3' + '  ' + self.RedYellowGreenState)
			elif (currSod > self.finishPhase[0]+(3*var.timeYellow)) and (currSod <= self.finishPhase[0]+(3*var.timeYellow)+var.minTimeGreen):
				self.RedYellowGreenState = self.phases[self.currAction]
			#   print('aca4' + '  ' + self.RedYellowGreenState)
			else:
				self.finishPhase = [-1, True]
			#   print('aca5')
			
	def applyPolicy(self, sec):	
		self.getJointState(sec)
		QM = np.zeros([len(self.actionPhases)])
		for act_i in self.actionPhases:
			for nb in self.neighbors:
				s = self.currJointState[nb]
				for act_j in var.agent_TLS[nb].actionPhases:
					aij = self.jointActions[nb].index((act_i, act_j))
					QM[act_i] += self.QValues[nb][s][aij+1] * self.M[nb][s][act_j+1]
		self.lastAction = self.currAction
		self.currAction = np.argmax(QM)
		self.finishPhase = [sec, False]
	
	def saveLearning(self, day, path):  
		for nb in self.neighbors:      
			df = pd.DataFrame(self.QValues[nb]); df.to_csv(path + 'QValues_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			df = pd.DataFrame(self.QAlpha[nb]); df.to_csv(path + 'QAlphas_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			df = pd.DataFrame(self.QCounts[nb]); df.to_csv(path + 'QCounts_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			df = pd.DataFrame(self.M[nb]); df.to_csv(path + 'M_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			df = pd.DataFrame(self.V[nb]); df.to_csv(path + 'V_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			
	
	
		
		
