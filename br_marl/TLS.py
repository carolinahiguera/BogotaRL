'''
Created on Nov 27, 2017

@author: carolina
'''
import var
import numpy as np
import pandas as pd
import random
from scipy.cluster.vq import vq, kmeans, whiten
path = '~/Documents/BogotaRL/ind_QLearning/csv_files_obs/'

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
		self.finishPhase = [-1, True]
		
		
		#Q matrix
		self.QValues = {}
		self.QCounts = {}
		self.QAlpha ={}
		
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
				
		# self.QValues = np.zeros((self.numStates,self.numActions))
		# self.QCounts = np.zeros((self.numStates,self.numActions))
		# self.QAlpha = np.ones((self.numStates,self.numActions))     
		
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishPhase = [-1, True]

	def ini4learning(self):
		aux = []
		df = pd.read_csv(path+'codebook_'+self.ID+'.csv')
		data = df.values
		self.numStates = len(data)
		for i in range(0,len(data)):
			aux.append(np.delete(data[i],0))
		self.codebook = np.array(aux)
		aux = []
		df = pd.read_csv(path+'normalize_'+self.ID+'.csv')
		data = df.values
		for i in range(0,len(data)):
			aux.append(data[i][1])
		self.normalize = np.array(aux)

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
		self.finishPhase = [0, False]
	
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
	
	def getState(self,currSod):
		state = [int(currSod/3600)+6]
		for j in range(0,len(self.listJunctions)):
			jID = self.listJunctions[j]
			for e in range(0,len(var.junctions[jID].edges)):
				state.append(self.queueEdgeTracker[j][e])
			for e in range(0,len(var.junctions[jID].edges)):
				state.append(self.waitingEdgeTracker[j][e])        
		state = np.array([state/self.normalize]) #verificar
		self.currState = vq(state, self.codebook)[0][0]


	# def getState(self):
	#   state = []
	#   for j in range(0,len(self.listJunctions)):
	#       jID = self.listJunctions[j]
	#       for e in range(0,len(var.junctions[jID].edges)):
	#           state.append(self.queueEdgeTracker[j][e])
	#       for e in range(0,len(var.junctions[jID].edges)):
	#           state.append(self.waitingEdgeTracker[j][e])        
	#   state = np.array(state)
	#   stateID = int(self.dictClusterObjects.predict(state.reshape(1,-1)))
	#   self.currState = self.mapDiscreteStates[stateID]
		
	
	def learnPolicy(self, currSod):
		self.getState(currSod)
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
		self.finishPhase = [sec, False]

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
	
	def saveLearning(self, day, path):        
		df = pd.DataFrame(self.QValues); df.to_csv(path + 'QValues_' + str(self.ID) + '_day' + str(day) +'.csv')
		df = pd.DataFrame(self.QAlpha); df.to_csv(path + 'QAlphas_' + str(self.ID) + '_day' + str(day) +'.csv')
		df = pd.DataFrame(self.QCounts); df.to_csv(path + 'QCounts_' + str(self.ID) + '_day' + str(day) +'.csv')
			
	
	
		
		