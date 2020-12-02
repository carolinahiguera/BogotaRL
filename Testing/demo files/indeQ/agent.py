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
    
    def __init__(self, ID, listLanes, listEdges, lengthEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors, beta, theta):
        self.SL = ID
        self.listLanes = listLanes
        self.listEdges = listEdges
        self.lengthEdges = lengthEdges
        self.numberLanes = numberLanes
        self.NESW = [1*(z>0) for z in numberLanes]
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
        self.numStates = 0
        #self.jointActions = {}
        self.numActions = len(self.actionPhases)
        #state, action, laststate
        self.currStateID = 0
        self.lastStateID = 0
        self.lastAction = 0
        #State discretization
        self.dictClusterObjects = {}
        self.numClustersTracker = {}            
        self.mapDiscreteStates = {}
        self.cluster_centers = {}
#         for n in self.neighbors:
#             self.numStates[n] = 0
#             self.jointActions[n] = {}
#             self.numActions[n] = {}
#             self.currJointStateID[n] = 0
#             self.lastJointStateID[n] = 0
#             self.lastJointAction[n] = 0
#             self.dictClusterObjects[n] = {}
#             self.numClustersTracker[n] = {}
#             self.mapDiscreteStates[n] = {}
        
        #Learning tables
        self.QValues = {}
        self.QCounts = {}
        self.QAlpha ={}
        
    
    def initAgent(self):  
        self.QValues = np.zeros((self.numStates,self.numActions))
        self.QCounts = np.zeros((self.numStates,self.numActions))
        self.QAlpha = np.ones((self.numStates,self.numActions))             
                    
        self.secsThisPhase = 0
        self.currPhaseID = 0
         
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward
    
    def learnPolicy(self, day, currHod):
        #get state
        state = []
        for edge in self.listEdges:
            state.append(self.queueTracker[edge])    
        for edge in self.listEdges:
            state.append(self.waitingTracker[edge])        
        state = np.array(state)
        a = self.currPhaseID
        stateSubID = int(self.dictClusterObjects[currHod][a].predict(state))
        self.currStateID = self.mapDiscreteStates[currHod][a][stateSubID]
        
        #update QValues
        s = self.lastStateID
        a = self.actionPhases.index(self.lastAction)
        r = self.currReward
        snew = self.currStateID        
        alpha = self.QAlpha[s,a]
        lastQ = self.QValues[s,a];
        maxQ = max(self.QValues[snew,])
        self.QValues[s,a] = lastQ + alpha*(r + self.gamma*maxQ - lastQ)        
        self.QCounts[s,a] += 1
        self.QAlpha[s,a] = 1.0/self.QCounts[s,a]
        
            
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
            ai = np.argmax(self.QValues[snew,])
            self.newPhaseID = self.actionPhases[ai]
        
        self.lastAction = self.currPhaseID
        self.lastStateID = self.currStateID
        
    
    def update(self):
        self.lastAction = self.newPhaseID
        self.lastStateID = self.currStateID
        
            
    def followPolicy(self, currHod):
        #get state
        h = currHod
        a = self.currPhaseID
        state = [h,a]
        for edge in self.listEdges:
            state.append(self.queueTracker[edge])    
        for edge in self.listEdges:
            state.append(self.waitingTracker[edge])        
        state = np.array(state)
        
        res = np.linalg.norm(state.T-self.cluster_centers, axis=1, ord=2)
        self.currStateID = np.argmin(res)
        
        #ai = np.argmax(self.QValues[self.currStateID,])
        ai = np.where(self.QValues[self.currStateID,]==np.max(self.QValues[self.currStateID,]))[0]
        i = np.random.randint(0,len(ai))
        act = ai[i]
        self.newPhaseID = self.actionPhases[act]        
        
    
    def loadKnowledge(self, day):
        self.cluster_centers = pd.read_csv('./states/recoveryStates_agt' + str(self.SL) +'.csv',
                                sep=' ', skipinitialspace=True, header=None)
        self.cluster_centers = self.cluster_centers.values
        df=pd.DataFrame.from_csv('./train/QValues_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        self.QValues = df.values
        
                    
        self.secsThisPhase = 0
        self.currPhaseID = 0
        
    
    def saveLearning(self, day):        
        df = pd.DataFrame(self.QValues); df.to_csv('QValues_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        df = pd.DataFrame(self.QAlpha); df.to_csv('QAlphas_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        df = pd.DataFrame(self.QCounts); df.to_csv('QCounts_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        