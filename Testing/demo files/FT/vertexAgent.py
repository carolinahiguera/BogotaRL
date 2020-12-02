'''
Created on 4/09/2016

@author: carolina
'''

class vertexAgent():
    
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
        self.numActions = len(actionPhases)
        #self.updatedState = False
        self.neighbors = neigbors
        self.numNeighbors = len(neigbors)
        
        #Reward properties
        self.beta = beta
        self.theta = theta 
        
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
    
    def initAgent(self):
        self.secsThisPhase = 0
        self.currPhaseID = 0
    
    def updateReward(self):
        reward = 0
        for key in self.listEdges:
            reward -= ((self.beta[0]*self.queueTracker[key])*self.theta[0] + (self.beta[1]*self.waitingTracker[key])**self.theta[1]) 
        self.currReward = reward