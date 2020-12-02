'''
Created on 22/09/2016

@author: carolina
'''
import numpy as np
import pandas as pd
import random
from random import randint
import itertools

import var

class agent():
    
    def __init__(self, ID, listLanes, listEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta):
        self.SL = ID
        self.listLanes = listLanes
        self.listEdges = listEdges
        self.numberLanes = numberLanes
        self.NESW = map(lambda z: 1*(z>0),numberLanes)
        self.numEdges = len(listEdges)
        self.numLanes = len(listLanes)
        self.actionPhases = actionPhases
        self.auxPhases = auxPhases
        self.planProgram = planProgram
        self.updatedState = False
        self.neighbors = neigbors
        self.numNeighbors = len(neigbors)
        
        #Reward properties
        self.beta = beta
        self.theta = theta 
        self.gamma = 0.9
        self.epsilon = 1.0
        
        #Almacenar informacion del agente por lane (colas, tiempo de espera)      
        self.laneQueueTracker = {}
        self.laneWaitingTracker = {} 
        for lane in self.listLanes:
            self.laneQueueTracker[lane] = 0
            self.laneWaitingTracker[lane] = 0            
        
        #Almacenar informacion del agente por edge (colas, tiempo de espera)  
        self.queueTracker = {}
        self.waitingTracker = {}
        for edge in self.listEdges:
            self.queueTracker[edge] = 0
            self.waitingTracker[edge] = 0
        
        self.secsThisPhase = 0
        self.currPhaseID = 0
        self.newPhaseID = 0
        self.currReward = 0
        
        #======== Data for each neighbor
        self.numStates = {}
        self.jointActions = {}
        self.numActions = {}
        #state, action, laststate
        self.currJointStateID = {}
        self.lastJointStateID = {}
        self.lastJointAction = {}
        #State discretization
        self.dictClusterObjects = {}
        self.numClustersTracker = {}            
        self.mapDiscreteStates = {}
        for n in self.neighbors:
            self.numStates[n] = 0
            self.jointActions[n] = {}
            self.numActions[n] = {}
            self.currJointStateID[n] = 0
            self.lastJointStateID[n] = 0
            self.lastJointAction[n] = 0
            self.dictClusterObjects[n] = {}
            self.numClustersTracker[n] = {}
            self.mapDiscreteStates[n] = {}
        
        #Learning tables
        self.QValues = {}
        self.QCounts = {}
        self.QAlpha ={}
        self.M = {}
        self.V = {}
        for n in self.neighbors:
            self.QValues[n] = {}
            self.QCounts[n] = {}
            self.QAlpha[n] = {}
            self.M[n] = {}
            self.V[n] = {}
    
    def initAgent(self):        
        for n in self.neighbors:
            self.jointActions[n] = list(itertools.product( var.agents[self.SL].actionPhases, var.agents[n].actionPhases ))
            self.numActions[n] = len(self.jointActions[n])
            self.QValues[n] = np.zeros((self.numStates[n],self.numActions[n]))
            self.QCounts[n] = np.zeros((self.numStates[n],self.numActions[n]))
            self.QAlpha[n] = np.ones((self.numStates[n],self.numActions[n]))
            nbAct = len(var.agents[n].actionPhases)
            self.M[n] = np.ones((self.numStates[n],nbAct))/nbAct
            self.V[n] = np.zeros((self.numStates[n],nbAct))
            
        self.secsThisPhase = 0
        self.currPhaseID = 0
    
    def getJointAction(self, nb):
        ph_i = self.currPhaseID
        ph_j = var.agents[nb].currPhaseID
        if(ph_i%2 != 0):
            ph_i -= 1
            
        if(ph_j%2 != 0):
            ph_j -= 1
            
        idx = self.jointActions[nb].index((ph_i, ph_j))
        return idx
    
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward
    
    def learnPolicy(self, day, currHod):
        for nb in self.neighbors:
            #get joint state
            state = []
            for edge in self.listEdges:
                state.append(self.queueTracker[edge])    
            for edge in self.listEdges:
                state.append(self.waitingTracker[edge])
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].queueTracker[edge])    
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].waitingTracker[edge])
            state = np.array(state)
            #get joint action
            ki_kj = self.getJointAction(nb)
            stateSubID = int(self.dictClusterObjects[nb][currHod][ki_kj].predict(state))
            self.currJointStateID[nb] = self.mapDiscreteStates[nb][currHod][ki_kj][stateSubID]
            
            #update probs of neighbour actions
            act_nb = var.agents[nb].actionPhases.index(var.agents[nb].currPhaseID)
            self.V[nb][self.lastJointStateID[nb], act_nb] += 1
            self.M[nb][self.lastJointStateID[nb], act_nb] = (self.V[nb][self.lastJointStateID[nb], act_nb])/(np.sum(self.V[nb][self.lastJointStateID[nb],]))
            
            #get self best response
            ai = -1
            maxBR = -float('Inf')
            for ph_i in self.actionPhases:
                aux = 0
                for ph_j in var.agents[nb].actionPhases:
                    ki_kj = self.jointActions[nb].index((ph_i, ph_j))
                    aux += self.QValues[nb][self.currJointStateID[nb],ki_kj] * self.M[nb][self.currJointStateID[nb], var.agents[nb].actionPhases.index(ph_j)]
                if(aux > maxBR):
                    maxBR = aux
                    ai = ph_i
            br = maxBR
            
            #update QValues
            s = self.lastJointStateID[nb]
            a = self.lastJointAction[nb]
            alpha = self.QAlpha[nb][s,a]
            self.QValues[nb][s,a] = (1-alpha)*self.QValues[nb][s,a] + alpha*(self.currReward + self.gamma*br)
            self.QCounts[nb][s,a] += 1
            self.QAlpha[nb][s,a] = 1.0/self.QCounts[nb][s,a]
            
        #decide if explore or exploit
        seed = (1.0*day)+(currHod/23.0)
        random.seed(seed)
        unigen = random.random()
        #self.epsilon = np.exp(-(1.0/30.0)*((1.0*day)+(currHod/23.0))) 
        self.epsilon = np.exp(-(1.0/60.0)*((1.0*day)+(currHod/23.0))) 
                
        if(unigen < self.epsilon): #Exploration?
            random.seed()
            ai = random.randint(0,len(self.actionPhases)-1)
            self.newPhaseID = self.actionPhases[ai]
        else:
            #get self best response
            ai = -1
            maxBR = -float('Inf')
            for ph_i in self.actionPhases:
                aux = 0
                for nb in self.neighbors:
                    for ph_j in var.agents[nb].actionPhases:
                        ki_kj = self.jointActions[nb].index((ph_i, ph_j))
                        aux += self.QValues[nb][self.currJointStateID[nb],ki_kj] * self.M[nb][self.currJointStateID[nb], var.agents[nb].actionPhases.index(ph_j)]
                if(aux > maxBR):
                    maxBR = aux
                    ai = ph_i
            self.newPhaseID = ai
        
    
    def updateJointAaction(self):
        for nb in self.neighbors:
            ai = self.newPhaseID
            aj = var.agents[nb].newPhaseID
            self.lastJointAction[nb] = self.jointActions[nb].index((ai, aj))
            self.lastJointStateID[nb] = self.currJointStateID[nb]
    
    def followPolicy(self, currHod):
        for nb in self.neighbors:
            #get joint state
            state = []
            for edge in self.listEdges:
                state.append(self.queueTracker[edge])    
            for edge in self.listEdges:
                state.append(self.waitingTracker[edge])
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].queueTracker[edge])    
            for edge in var.agents[nb].listEdges:
                state.append(var.agents[nb].waitingTracker[edge])
            state = np.array(state)
            #get joint action
            ki_kj = self.getJointAction(nb)
            stateSubID = int(self.dictClusterObjects[nb][currHod][ki_kj].predict(state))
            self.currJointStateID[nb] = self.mapDiscreteStates[nb][currHod][ki_kj][stateSubID]
            if(self.currJointStateID[nb] >= np.shape(self.QValues[nb])[0]):
                self.currJointStateID[nb] = np.shape(self.QValues[nb])[0]-1
        #get self best response
        ai = -1
        maxBR = -float('Inf')
        for ph_i in self.actionPhases:
            aux = 0
            for nb in self.neighbors:
                for ph_j in var.agents[nb].actionPhases:
                    ki_kj = self.jointActions[nb].index((ph_i, ph_j))
                    aux += self.QValues[nb][self.currJointStateID[nb],ki_kj] * self.M[nb][self.currJointStateID[nb], var.agents[nb].actionPhases.index(ph_j)]
            if(aux > maxBR):
                maxBR = aux
                ai = ph_i
        self.newPhaseID = ai
    
    def loadKnowledge(self, day):
        for nb in self.neighbors:
            self.jointActions[nb] = list(itertools.product( var.agents[self.SL].actionPhases, var.agents[nb].actionPhases ))
            self.numActions[nb] = len(self.jointActions[nb])
            df=pd.DataFrame.from_csv('QValues_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) +'.csv')
            self.QValues[nb] = df.values
            df=pd.DataFrame.from_csv('QAlphas_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) +'.csv')
            self.QAlpha[nb] = df.values
            df=pd.DataFrame.from_csv('QCounts_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) +'.csv')
            self.QCounts[nb] = df.values
            df=pd.DataFrame.from_csv('M_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            self.M[nb] = df.values
            df=pd.DataFrame.from_csv('V_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            self.V[nb] = df.values
            
        self.secsThisPhase = 0
        self.currPhaseID = 0
        
    
    def saveLearning(self, day):
        for nb in self.neighbors:
            df = pd.DataFrame(self.QValues[nb]); df.to_csv('QValues_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) +'.csv')
            df = pd.DataFrame(self.QAlpha[nb]); df.to_csv('QAlphas_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            df = pd.DataFrame(self.QCounts[nb]); df.to_csv('QCounts_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            df = pd.DataFrame(self.M[nb]); df.to_csv('M_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv')
            df = pd.DataFrame(self.V[nb]); df.to_csv('V_agt' + str(self.SL) + '_' +  str(nb) + '_day' + str(day) + '.csv') 
