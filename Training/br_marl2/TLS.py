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
		self.timeInGreen = 0
		self.validPrevStates = False

		#Almacena informacion del agente por interseccion (colas, tiempo de espera)  
		self.queueEdgeTracker = {}
		self.waitingEdgeTracker = {}
		self.speedEdgeTracker = {}
		self.queueLaneTracker = {}
		self.waitingLaneTracker = {}  
		self.speedLaneTracker = {} 

		#Parametros del aprendizaje
		self.secsOfTF = var.pTransfer*var.episodes*var.secondsInDay
		self.secsOfBR = (1-var.pTransfer)*var.episodes*var.secondsInDay

		self.alpha_FT = var.alpha_FT
		self.alpha_BR_start = var.alpha_BR_start
		self.alpha_BR_end = var.alpha_BR_end	
		self.alpha_expFactor = np.log(alpha_BR_start/alpha_BR_end)

		self.epsilon_BR_start = var.epsilon_BR_start
		self.epsilon_BR_end = var.epsilon_BR_end
		self.epsilon_expFactor = np.log(epsilon_BR_start/epsilon_BR_end)
		self.epsilon = 0.0

		self.gamma = 0.9
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
		self.ini_frames()
		self.load_observationData()

		if var.start_episode==0:
			for nb in self.neighbors:
				self.QValues[nb] = np.zeros((self.numJointStates[nb],self.numJointActions[nb]))			
				nbAct = len(var.agent_TLS[nb].actionPhases)
				self.V[nb] = np.zeros((self.numJointStates[nb],nbAct))
				self.M[nb] = np.ones((self.numJointStates[nb],nbAct))/nbAct
		else:
			day = var.start_episode - 1
			self.load_learningData(var.trainPath, day)

	def ini_frames(self):
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

	def load_observationData(self):
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

	def load_learningData(self, path_train, day):
		for nb in self.neighbors:
			df = pd.read_csv(path_train+'QValues_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			if df.values.shape[1] > self.numJointActions[nb]:
				self.QValues[nb] = df.values[:,1:]
			else:
				self.QValues[nb] = df.values

			nbAct = len(var.agent_TLS[nb].actionPhases)
			df = pd.read_csv(path_train+'V_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			if df.values.shape[1] > nbAct:
				self.V[nb] = df.values[:,1:]
			else:
				self.V[nb] = df.values

			df = pd.read_csv(path_train+'M_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv')
			if df.values.shape[1] > nbAct:
				self.M[nb] = df.values[:,1:]
			else:
				self.M[nb] = df.values

	def set_first_action(self):	
		seed = random.random()
		random.seed(seed)
		self.currAction = random.randint(0,len(self.actionPhases)-1) 
		self.lastAction = self.currAction
		self.RedYellowGreenState = self.phases[self.currAction]
		self.finishPhase = [0, False]


			#self.getJointState(0)

	def ft_get_phase(self,currSod):
		if currSod < 18000:
			#execute plan 2
			action = self.plan2[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan2)
			self.change_action = False
			if self.RedYellowGreenState in self.phases:
				if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
					self.change_action = True
					self.updateStateAction()
					self.currAction = self.phases.index(self.RedYellowGreenState)				
					self.getJointState(currSod)
		elif currSod>=18000 and currSod<32400:
			#execute plan 3
			if currSod == 18000:
				self.counterPlan = 0
			action = self.plan3[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan3)
			self.change_action = False
			if self.RedYellowGreenState in self.phases:
				if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
					self.change_action = True
					self.updateStateAction()
					self.currAction = self.phases.index(self.RedYellowGreenState)				
					self.getJointState(currSod)
		else:
			#execute plan 4
			if currSod == 32400:
				self.counterPlan = 0
			action = self.plan4[self.counterPlan]
			self.finishPhase = [currSod+action[0], False]
			self.RedYellowGreenState = action[1]
			self.counterPlan = (self.counterPlan+1)%len(self.plan4)
			self.change_action = False
			if self.RedYellowGreenState in self.phases:
				if self.phases.index(self.RedYellowGreenState) in self.actionPhases:
					self.change_action = True
					self.updateStateAction()
					self.currAction = self.phases.index(self.RedYellowGreenState)				
					self.getJointState(currSod)

	def ft_check_complete_phase(self, currSod):
		if currSod == self.finishPhase[0]:
			self.finishPhase = [-1, True]

	#Q LEARNING FUNTIONS-------------------------------------------------

	def getObservation_NB(self, nb, currSod):
	    #estado del agente tls
	    stateDataEntry = [int(currSod/3600)+6]
	    for j in range(0,len(self.listJunctions)):
	        jID = self.listJunctions[j]
	        for e in range(0,len(var.junctions[jID].edges)):
	            stateDataEntry.append(self.queueEdgeTracker[j][e])
	    for j in range(0,len(self.listJunctions)):
	        jID = self.listJunctions[j]
	        for e in range(0,len(var.junctions[jID].edges)):
	            stateDataEntry.append(self.waitingEdgeTracker[j][e])
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

	def updateStateAction(self):
		self.lastAction = self.currAction
		#self.validPrevStates = True
		for nb in self.neighbors:
			self.lastJointAction[nb] = self.currJointAction[nb]
			self.lastJointState[nb] = self.currJointState[nb]
			#if self.lastJointAction[nb]==None or self.lastJointState[nb]==None:
			#	self.validPrevStates = False

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

	def getBR_ft(self, nb, s):
		QM = np.zeros([len(self.actionPhases)])
		for act_i in self.actionPhases:
			for act_j in var.agent_TLS[nb].actionPhases:
				aij = self.jointActions[nb].index((act_i, act_j))
				QM[act_i] += self.QValues[nb][s][aij] * self.M[nb][s][act_j]
		ai_new = self.jointActions[nb][self.currJointAction[nb]][0]
		br = QM[ai_new]
		return br

	def get_alpha(self, currSod, day):
		totalSec = day*var.secondsInDay + currSod
		alpha = self.alpha_BR_start * np.exp(-self.alpha_expFactor*(totalSec-self.secsOfTF)/self.secsOfBR)
		#min = int(round(currSod/60.0))
		#alpha = self.alpha_FT * np.exp(-(1.0/180.0)*((1.0*day)+(min/60.0))) 
		return alpha

	def updateQValue(self, currSod):
		self.updateStateAction()
		self.getJointState(currSod)		
		for nb in self.neighbors:
			s = self.lastJointState[nb]
			a = self.lastJointAction[nb]
			s_ = self.currJointState[nb]
			r = self.currReward

			act_j = self.jointActions[nb][a][1]
			self.V[nb][s, act_j] += 1.0
			self.M[nb][s, ] = self.V[nb][s, ] / np.sum(self.V[nb][s,])
			br = self.getBR_ft(nb, s_)
			alpha = self.alpha_FT
			lastQ = self.QValues[nb][s][a]
			self.QValues[nb][s][a] = lastQ + alpha*(r + self.gamma*br - lastQ)

	def getBR(self, nb, s):
		QM = np.zeros([len(self.actionPhases)])
		for act_i in self.actionPhases:
			for act_j in var.agent_TLS[nb].actionPhases:
				aij = self.jointActions[nb].index((act_i, act_j))
				QM[act_i] += self.QValues[nb][s,aij] * self.M[nb][s,act_j]
		br = np.max(QM)
		return br

	
	def learnPolicy(self, currSod, day):
		self.getJointState(currSod)
		for nb in self.neighbors:
			s = self.lastJointState[nb]
			a = self.lastJointAction[nb]
			s_ = self.currJointState[nb]
			if s==None or a==None or s_==None:
				continue
			r = self.currReward			
			act_j = self.jointActions[nb][a][1]
			self.V[nb][s, act_j] += 1.0
			self.M[nb][s, ] = self.V[nb][s, ] / np.sum(self.V[nb][s,])

			br = self.getBR(nb, s_)
			alpha = self.get_alpha(currSod, day)
			lastQ = self.QValues[nb][s][a]
			self.QValues[nb][s][a] = lastQ + alpha*(r + self.gamma*br - lastQ)			
	
	def getAction(self, day, sec):
		min = int(round(sec/60.0))
		seed = (1.0*day)+(sec/60.0)
		random.seed(seed)
		unigen = random.random()        
		#self.epsilon = np.exp(-(1.0/180.0)*((1.0*day)+(min/60.0))) 

		totalSec = day*var.secondsInDay + sec
		self.epsilon = self.epsilon_BR_start * np.exp(-self.epsilon_expFactor*(totalSec-self.secsOfTF)/self.secsOfBR)

		# self.epsilon = np.exp(-(1.0/130.0)*((1.0*day)+(min/60.0))) 
		# self.epsilon = 0.3
		
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
						QM[act_i] += self.QValues[nb][s][aij] * self.M[nb][s][act_j]
			self.currAction = np.argmax(QM)
		self.finishPhase = [sec, False]
		if self.lastAction == self.currAction:
			self.timeInGreen += var.minTimeGreen
		else: 
			self.timeInGreen = 0
		if self.timeInGreen > var.maxTimeGreen:
			self.currAction = 1 if (self.currAction==0) else 0

	def applyPolicy(self, sec):	
		self.getJointState(sec)
		QM = np.zeros([len(self.actionPhases)])		
		for act_i in self.actionPhases:
			for nb in self.neighbors:
				s = self.currJointState[nb]
				for act_j in var.agent_TLS[nb].actionPhases:
					aij = self.jointActions[nb].index((act_i, act_j))
					QM[act_i] += self.QValues[nb][s,aij] * self.M[nb][s,act_j]
		self.lastAction = self.currAction
		self.currAction = np.argmax(QM)
		self.finishPhase = [sec, False]
		if self.lastAction == self.currAction:
			self.timeInGreen += var.minTimeGreen
		else: 
			self.timeInGreen = 0
		if self.timeInGreen > var.maxTimeGreen:
			self.currAction = 1 if (self.currAction==0) else 0	

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

	#SAVING
	def saveLearning(self, day, path):  
		for nb in self.neighbors:      
			df = pd.DataFrame(self.QValues[nb]); df.to_csv(path + 'QValues_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv', index=False)
			df = pd.DataFrame(self.M[nb]); df.to_csv(path + 'M_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv', index=False)
			df = pd.DataFrame(self.V[nb]); df.to_csv(path + 'V_' + str(self.ID) +'_' + nb + '_day' + str(day) +'.csv', index=False)
			



		
		