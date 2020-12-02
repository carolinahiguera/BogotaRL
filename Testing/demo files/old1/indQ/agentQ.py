'''
Created on 4/09/2016

@author: carolina
'''
import numpy as np
import pandas as pd
import pickle

class agentQ():
    
    def __init__(self, ID, listLanes, listEdges, lengthEdges, numberLanes, actionPhases, auxPhases, planProgram, neigbors):
        self.SL = ID
        self.listLanes = listLanes
        self.listEdges = listEdges
        self.lengthEdges = lengthEdges
        self.numberLanes = numberLanes
        self.NESW = map(lambda z: 1*(z>0),numberLanes)
        self.numEdges = len(listEdges)
        self.numLanes = len(listLanes)
        self.actionPhases = actionPhases
        self.auxPhases = auxPhases
        self.planProgram = planProgram
        self.numActions = len(actionPhases)
        self.updatedState = False
        self.neighbors = neigbors
        self.numNeighbors = len(neigbors)
        
        #Reward properties
        self.beta = [1,2]
        self.theta = [1.75, 1.75] 
        
        #Almacenar informacion del agente por lane (colas, tiempo de espera)      
        self.laneQueueTracker = {}
        self.laneWaitingTracker = {} 
        self.laneSpeedTracker = {}
        for lane in self.listLanes:
            self.laneQueueTracker[lane] = 0
            self.laneWaitingTracker[lane] = 0  
            self.laneSpeedTracker[lane] = 0          
        
        #Almacenar informacion del agente por edge (colas, tiempo de espera)  
        self.queueTracker = {}
        self.waitingTracker = {}
        self.speedTracker = {}
        for edge in self.listEdges:
            self.queueTracker[edge] = 0
            self.waitingTracker[edge] = 0
            self.speedTracker[edge] = 0
        
        self.secsThisPhase = 0
        self.currPhaseID = 0
        self.newPhaseID = 0
        self.currReward = 0
    
    #======== Data for each neighbor
        self.numStates = 0
        self.numActions = len(self.actionPhases)
        self.currStateID = 0
        self.lastStateID = 0
        self.lastAction = 0
        self.dictClusterObjects = {}
        self.numClustersTracker = {}            
        self.mapDiscreteStates = {}
        self.cluster_centers = None
       
        #Learning tables
        self.QValues = {}
        
        
    
    def initAgent(self):  
        self.QValues = np.zeros((self.numStates,self.numActions))
        self.secsThisPhase = 0
        self.currPhaseID = 0
         
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward
    
            
    def followPolicy(self, currHod):
        #get state
        h = currHod
        a = self.currPhaseID
        state = [h, a]
        for edge in self.listEdges:
            state.append(self.queueTracker[edge])    
        for edge in self.listEdges:
            state.append(self.waitingTracker[edge])        
        state = np.array(state)  

        res = np.linalg.norm(state.T-self.cluster_centers, axis=1, ord=2)
        self.currStateID = np.argmin(res)      

        #stateSubID = int(self.dictClusterObjects[currHod][a].predict(state))
        #self.currStateID = self.mapDiscreteStates[currHod][a][stateSubID]
        
        ai = np.argmax(self.QValues[self.currStateID,])
        self.newPhaseID = self.actionPhases[ai]    
    
    def update(self):
        self.lastAction = self.newPhaseID
        self.lastStateID = self.currStateID
    
    def loadKnowledge(self, day):
        self.cluster_centers = pd.read_csv('./states/recoveryStates_agt' + str(self.SL) +'.csv',
                                sep=' ', skipinitialspace=True, header=None)
        self.cluster_centers = self.cluster_centers.values
        df=pd.DataFrame.from_csv('./train/QValues_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        self.QValues = df.values
        # df=pd.DataFrame.from_csv('QAlphas_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        # self.QAlpha = df.values[:,1:]
        # df=pd.DataFrame.from_csv('QCounts_agt' + str(self.SL) + '_day' + str(day) +'.csv')
        # self.QCounts = df.values[:,1:]
                    
        self.secsThisPhase = 0
        self.currPhaseID = 0