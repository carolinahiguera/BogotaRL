'''
Created on Nov 27, 2017

@author: carolina
'''
import var
import numpy as np
import pandas as pd
import random

class TLS(object):
	'''
	classdocs
	'''


	def __init__(self, ID, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp):
		self.ID = ID
		self.listJunctions = listJunctions
		self.phases = phases
		self.actionPhases = actionPhases
		self.auxPhases = auxPhases
		
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
		self.currState = -1
		self.lastAction = -1
		self.lastState = -1
		self.RedYellowGreenState = ''
		self.beta = beta
		self.theta = theta        
		self.exp = exp
		self.gamma = 0.9
		self.epsilon = 1.0
		self.setInYellow = -1
		self.finishAuxPhase = True
		
		
		#Q matrix
		self.QValues = {}
		self.QCounts = {}
		self.QAlpha ={}
		
		#Discretizacion de espacio de estados
		self.numStates = 0
		self.numActions = len(self.actionPhases)
		self.dictClusterObjects = {}
		self.numClustersTracker = 0         
		self.mapDiscreteStates = {}
		
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
				
		self.QValues = np.zeros((self.numStates,self.numActions))
		self.QCounts = np.zeros((self.numStates,self.numActions))
		self.QAlpha = np.ones((self.numStates,self.numActions))     
		
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishAuxPhase = True
	
	def updateStateAction(self):
		self.lastAction = self.currAction
		self.lastState = self.currState        
	
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
	
	def getState(self):
		state = []
		for j in range(0,len(self.listJunctions)):
			jID = self.listJunctions[j]
			for e in range(0,len(var.junctions[jID].edges)):
				state.append(self.queueEdgeTracker[j][e])
			for e in range(0,len(var.junctions[jID].edges)):
				state.append(self.waitingEdgeTracker[j][e])        
		state = np.array(state)
		stateID = int(self.dictClusterObjects.predict(state.reshape(1,-1)))
		self.currState = self.mapDiscreteStates[stateID]
		
	
	def learnPolicy(self):
		self.getState()
		s = self.lastState
		a = self.lastAction
		s_ = self.currState
		r = self.currReward
		alpha = self.QAlpha[s,a]
		lastQ = self.QValues[s,a]
		maxQ = max(self.QValues[s_, ])
		self.QValues[s,a] = lastQ + alpha*(r + self.gamma*maxQ - lastQ)
		self.QCounts[s,a] += 1.0
		self.QAlpha[s,a] = 1.0/self.QCounts[s,a]
	
	def getAction(self, day, sec):
		min = int(round(sec/60.0))
		seed = (1.0*day)+(sec/60.0)
		random.seed(seed)
		unigen = random.random()        
		self.epsilon = np.exp(-(1.0/180.0)*((1.0*day)+(min/60.0))) 
		
		if(unigen < self.epsilon):
			#Explorar
			self.currAction = random.randint(0,len(self.actionPhases)-1) 
		else: 
			#Explotar
			Qmax = max(self.QValues[self.currState, ])
			opt_act = [x for x in range(0,self.numActions) if self.QValues[self.currState,x]==Qmax]
			idx = random.randint(0,len(opt_act)-1) 
			self.currAction = opt_act[idx]          
			
		if(self.currAction != self.lastAction):
			self.setInYellow = sec
			self.finishAuxPhase = False
			
	
	def setPhase(self, currSod):
		aux_phase = self.auxPhases[self.lastAction][self.currAction]
		if(not(type(aux_phase)==list)):
			if currSod <= self.setInYellow+var.timeYellow:
				self.RedYellowGreenState = self.phases[aux_phase]
			if (currSod > self.setInYellow+var.timeYellow) and (currSod <= self.setInYellow+var.timeYellow+var.minTimeGreen)
				self.RedYellowGreenState = self.phases[self.currAction]
			else:
				self.setInYellow = -1
				self.finishAuxPhase = True
		else:
			if currSod <= self.setInYellow+var.timeYellow:
				self.RedYellowGreenState = self.phases[aux_phase[0]]
			if (currSod > self.setInYellow+var.timeYellow) and (currSod <= self.setInYellow+(2*var.timeYellow)):
				self.RedYellowGreenState = self.phases[aux_phase[1]]
			if (currSod > self.setInYellow+(2*var.timeYellow)) and (currSod < self.setInYellow+(2*var.timeYellow)+var.minTimeGreen):
				self.RedYellowGreenState = self.phases[self.currAction]
			else:
				self.setInYellow = -1
				self.finishAuxPhase = True



	# def setPhase(self, opt):
	# 	aux_phase = self.auxPhases[self.lastAction][self.currAction]
	# 	if(opt == 0):                        
	# 		if(not(type(aux_phase)==list)):   
	# 			self.RedYellowGreenState = self.phases[aux_phase]
	# 		else:                   
	# 			self.RedYellowGreenState = self.phases[aux_phase[0]] 
	# 	if(opt == 1):
	# 		self.RedYellowGreenState = self.phases[aux_phase[1]] 
	# 	if(opt == 2):
	# 		self.RedYellowGreenState = self.phases[self.currAction]
	# 		self.setInYellow = -1
	# 	return aux_phase

	
	def applyPolicy(self, sec):
		self.lastAction = self.currAction
		self.currState = self.getState()
		Qmax = max(self.QValues[self.currState, ])
		opt_act = [x for x in range(0,self.numActions) if self.QValues[self.currState,x]==Qmax]
		idx = random.randint(0,len(opt_act)-1) 
		self.currAction = opt_act[idx]
		if(sec > 0):
			if(self.currAction != self.lastAction):
				self.setInYellow = sec
				self.finishAuxPhase = False
	
	def saveLearning(self, day):        
		df = pd.DataFrame(self.QValues); df.to_csv('./csv_files_learning/QValues_' + str(self.ID) + '_day' + str(day) +'.csv')
		df = pd.DataFrame(self.QAlpha); df.to_csv('./csv_files_learning/QAlphas_' + str(self.ID) + '_day' + str(day) +'.csv')
		df = pd.DataFrame(self.QCounts); df.to_csv('./csv_files_learning/QCounts_' + str(self.ID) + '_day' + str(day) +'.csv')
			
	
	
		
		